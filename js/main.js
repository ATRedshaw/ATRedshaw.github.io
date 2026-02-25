// Main JavaScript file for Shared Logic

// --- Constants & Config ---
const DATA_DIR = 'data/';
const CONTENT_DIR = 'content/';

// --- Utility Functions ---

/**
 * Fetch and parse a YAML file.
 * @param {string} filename - The name of the YAML file in the data directory.
 * @returns {Promise<Object>} - The parsed JavaScript object.
 */
async function loadYamlData(filename) {
    try {
        const response = await fetch(`${DATA_DIR}${filename}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch ${filename}: ${response.statusText}`);
        }
        const text = await response.text();
        return jsyaml.load(text);
    } catch (error) {
        console.error('Error loading YAML data:', error);
        return null;
    }
}

/**
 * Fetch and return text content (Markdown).
 * @param {string} filepath - Path to the markdown file.
 * @returns {Promise<string>}
 */
async function loadMarkdown(filepath) {
    try {
        const response = await fetch(filepath);
        if (!response.ok) {
            throw new Error(`Failed to fetch ${filepath}: ${response.statusText}`);
        }
        return await response.text();
    } catch (error) {
        console.error('Error loading markdown:', error);
        return '';
    }
}

// --- UI / DOM Functions ---

// 1. Navbar Logic
function initNavbar() {
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // Highlight active link based on current URL
    const currentPath = window.location.pathname.split('/').pop() || 'index.html';
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('text-blue-600', 'font-semibold');
        } else {
            link.classList.remove('text-blue-600', 'font-semibold');
            link.classList.add('text-slate-600', 'hover:text-blue-500');
        }
    });
}

// 2. Footer Logic
async function initFooter() {
    const footerSocials = document.getElementById('footer-socials');
    const currentYearSpan = document.getElementById('current-year');
    
    if (currentYearSpan) {
        currentYearSpan.textContent = new Date().getFullYear();
    }

    // Load social links from site.yaml
    const siteData = await loadYamlData('site.yaml');
    if (siteData && siteData.social && footerSocials) {
        // Clear existing static links if any, or append
        footerSocials.innerHTML = ''; 

        // Helper to create icon SVG (simplified) or use FontAwesome classes if loaded
        // Using Lucide (CDN in HTML) pattern: <i data-lucide="..."></i> then lucide.createIcons()
        
        Object.entries(siteData.social).forEach(([platform, url]) => {
            if (!url) return;
            
            const link = document.createElement('a');
            link.href = url;
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
            link.className = 'text-slate-400 hover:text-white transition-colors duration-300';
            link.setAttribute('aria-label', platform);
            
            // Map platform to icon name (assuming Lucide icons used)
            let iconName = 'link';
            if (platform === 'github') iconName = 'github';
            if (platform === 'linkedin') iconName = 'linkedin';
            if (platform === 'twitter') iconName = 'twitter';
            if (platform === 'email') iconName = 'mail';

            link.innerHTML = `<i data-lucide="${iconName}" class="w-5 h-5"></i>`;
            footerSocials.appendChild(link);
        });
        
        // Re-initialize icons if using Lucide
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }
}

// 3. Scroll Animations
function initScrollAnimations() {
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                entry.target.classList.remove('opacity-0', 'translate-y-8'); // Remove Tailwind utility hides if used
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    const sections = document.querySelectorAll('.fade-in-section');
    sections.forEach(section => {
        observer.observe(section);
    });
}

// 4. Modal Logic (Shared)
const modalOverlay = document.getElementById('modal-overlay');
const modalContent = document.getElementById('modal-content');
const modalBody = document.getElementById('modal-body');
const modalCloseBtn = document.getElementById('modal-close');

function openModal(contentHtml) {
    if (!modalOverlay || !modalBody) return;
    
    modalBody.innerHTML = contentHtml;
    modalOverlay.classList.remove('hidden');
    // Allow a small tick for display to apply before opacity transition
    setTimeout(() => {
        modalOverlay.classList.remove('opacity-0');
        modalContent.classList.remove('scale-95', 'opacity-0');
        modalContent.classList.add('scale-100', 'opacity-100');
    }, 10);
    
    document.body.style.overflow = 'hidden'; // Lock scroll

    // Re-highlight code blocks inside modal
    if (typeof hljs !== 'undefined') {
        modalBody.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
    }
}

function closeModal() {
    if (!modalOverlay) return;

    modalOverlay.classList.add('opacity-0');
    modalContent.classList.remove('scale-100', 'opacity-100');
    modalContent.classList.add('scale-95', 'opacity-0');
    
    setTimeout(() => {
        modalOverlay.classList.add('hidden');
        document.body.style.overflow = ''; // Unlock scroll
        if (modalBody) modalBody.innerHTML = ''; // Clear content
    }, 300); // Match transition duration
}

function initModal() {
    if (modalCloseBtn) {
        modalCloseBtn.addEventListener('click', closeModal);
    }
    if (modalOverlay) {
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) {
                closeModal();
            }
        });
    }
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !modalOverlay.classList.contains('hidden')) {
            closeModal();
        }
    });
}


// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    initNavbar();
    initFooter();
    initScrollAnimations();
    initModal();
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
});
