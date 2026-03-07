// Main JavaScript file for Shared Logic

// --- Constants & Config ---
const DATA_DIR = 'data/';
const CONTENT_DIR = 'content/';

// --- Utility Functions ---

async function loadYamlData(filename) {
    try {
        const response = await fetch(`${DATA_DIR}${filename}`);
        if (!response.ok) throw new Error(`Failed to fetch ${filename}`);
        const text = await response.text();
        return jsyaml.load(text);
    } catch (error) {
        console.error('Error loading YAML data:', error);
        return null;
    }
}

async function loadMarkdown(filepath) {
    try {
        const response = await fetch(filepath);
        if (!response.ok) throw new Error(`Failed to fetch ${filepath}`);
        return await response.text();
    } catch (error) {
        console.error('Error loading markdown:', error);
        return '';
    }
}

/**
 * Parses a markdown string to HTML, safely handling LaTeX math expressions.
 *
 * Display math ($$...$$) and inline math ($...$) are stashed before the
 * markdown parser runs — preventing it from mangling LaTeX syntax such as
 * subscript underscores and pipe characters — then restored as rendered
 * KaTeX output. Falls back to a <code> block if KaTeX is unavailable.
 *
 * @param {string} mdText - Raw markdown string.
 * @returns {string} Rendered HTML.
 */
function parseMarkdown(mdText) {
    const stash = [];

    const stashMath = (content, displayMode) => {
        const placeholder = `MATHPLACEHOLDER${stash.length}END`;
        stash.push({ content, displayMode });
        // Surround display-math placeholders with blank lines so marked
        // treats them as their own paragraph rather than inline text.
        return displayMode ? `\n\n${placeholder}\n\n` : placeholder;
    };

    // Stash display math first to avoid the $$ being caught by the inline pass.
    let processed = mdText.replace(/\$\$([\s\S]+?)\$\$/g, (_, math) => stashMath(math, true));
    // Stash inline math, excluding $ adjacent to another $ (already handled).
    processed = processed.replace(/(?<!\$)\$([^$\n]+?)\$(?!\$)/g, (_, math) => stashMath(math, false));

    let html = marked.parse(processed);

    html = html.replace(/MATHPLACEHOLDER(\d+)END/g, (_, idx) => {
        const { content, displayMode } = stash[parseInt(idx, 10)];
        if (typeof katex !== 'undefined') {
            try {
                return katex.renderToString(content.trim(), { displayMode, throwOnError: false });
            } catch {
                return `<code>${content}</code>`;
            }
        }
        return displayMode
            ? `<pre class="math-block"><code>${content}</code></pre>`
            : `<code>${content}</code>`;
    });

    return html;
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
        // Simple exact match or specialized logic
        if (link.getAttribute('href') === currentPath) {
            // Active state
            link.classList.remove('text-porcelain/70');
            link.classList.add('text-terracotta');
        } else {
            // Inactive state
            link.classList.remove('text-terracotta');
            link.classList.add('text-porcelain/70');
        }
    });
}

// 2. Footer & Socials Logic
async function initFooter() {
    const footerSocials = document.getElementById('footer-socials');
    const currentYearSpan = document.getElementById('current-year');
    
    if (currentYearSpan) {
        currentYearSpan.textContent = new Date().getFullYear();
    }

    // Load social links from site.yaml
    const siteData = await loadYamlData('site.yaml');
    if (siteData && siteData.social) {
        
        const renderSocials = (container) => {
            if (!container) return;
            container.innerHTML = ''; 
            
            Object.entries(siteData.social).forEach(([platform, url]) => {
                if (!url) return;
                
                const link = document.createElement('a');
                link.href = url;
                link.target = '_blank';
                link.rel = 'noopener noreferrer';
                link.className = 'text-porcelain/40 hover:text-terracotta transition-colors duration-300';
                link.setAttribute('aria-label', platform);
                
                let iconName = 'link';
                if (platform === 'github') iconName = 'github';
                if (platform === 'linkedin') iconName = 'linkedin';
                if (platform === 'twitter') iconName = 'twitter';
                if (platform === 'email') iconName = 'mail';

                link.innerHTML = `<i data-lucide="${iconName}" class="w-5 h-5"></i>`;
                container.appendChild(link);
            });
             if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
        };

        renderSocials(footerSocials);
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
// Assumes HTML structure: #modal-overlay -> #modal-content -> #modal-body + #modal-close
const modalOverlay = document.getElementById('modal-overlay');
const modalContent = document.getElementById('modal-content');
const modalBody = document.getElementById('modal-body');
const modalCloseBtn = document.getElementById('modal-close');

function openModal(contentHtml) {
    if (!modalOverlay || !modalBody) return;
    
    // Set content
    modalBody.innerHTML = contentHtml;
    
    // Show overlay
    modalOverlay.classList.remove('hidden');
    
    // Trigger animations
    setTimeout(() => {
        modalOverlay.classList.remove('opacity-0');
        if(modalContent) {
            modalContent.classList.remove('scale-95', 'opacity-0');
            modalContent.classList.add('scale-100', 'opacity-100');
        }
    }, 10);
    
    document.body.style.overflow = 'hidden'; // Lock scroll

    // Highlight code
    if (typeof hljs !== 'undefined') {
        modalBody.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
    }
    
    // Initialize icons in modal
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

function closeModal() {
    if (!modalOverlay) return;

    modalOverlay.classList.add('opacity-0');
    if(modalContent) {
        modalContent.classList.remove('scale-100', 'opacity-100');
        modalContent.classList.add('scale-95', 'opacity-0');
    }
    
    setTimeout(() => {
        modalOverlay.classList.add('hidden');
        document.body.style.overflow = ''; // Unlock scroll
        if (modalBody) modalBody.innerHTML = ''; // Clear content
    }, 300);
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
