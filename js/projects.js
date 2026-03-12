// Projects Page Logic

let allProjects = [];

document.addEventListener('DOMContentLoaded', async () => {
    const data = await loadYamlData('projects.yaml');
    if (!data || !data.projects) return;

    allProjects = data.projects;
    setupFilters();
    renderProjects(allProjects);

    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

    checkDeepLink();
    initProjectModalCloseHook();
});

function setupFilters() {
    const filterContainer = document.getElementById('filter-container');
    if (!filterContainer) return;

    // Extract unique tags
    const tagsSet = new Set();
    allProjects.forEach(p => p.tags.forEach(t => tagsSet.add(t)));
    const tags = Array.from(tagsSet).sort();
    
    // Create Dropdown (Minimalist Design)
    const select = document.createElement('select');
    select.className = 'bg-midnight text-porcelain border border-white/10 px-6 py-3 font-mono text-xs uppercase tracking-widest focus:outline-none focus:border-terracotta transition-colors cursor-pointer appearance-none pr-10 relative z-10';
    select.style.backgroundImage = 'url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'16\' height=\'16\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'%23F4F1EA\' stroke-width=\'2\' stroke-linecap=\'round\' stroke-linejoin=\'round\'%3E%3Cpolyline points=\'6 9 12 15 18 9\'%3E%3C/polyline%3E%3C/svg%3E")';
    select.style.backgroundRepeat = 'no-repeat';
    select.style.backgroundPosition = 'right 1rem center';
    
    let optionsHtml = `<option value="all">All Projects</option>`;
    tags.forEach(tag => {
        optionsHtml += `<option value="${tag}">${tag}</option>`;
    });

    select.innerHTML = optionsHtml;
    filterContainer.innerHTML = '';
    filterContainer.appendChild(select);

    // Add Event Listener
    select.addEventListener('change', (e) => {
        filterProjects(e.target.value);
    });
}

function filterProjects(filter) {
    if (filter === 'all') {
        renderProjects(allProjects);
    } else {
        const filtered = allProjects.filter(p => p.tags.includes(filter));
        renderProjects(filtered);
    }
}

function renderProjects(projects) {
    const grid = document.getElementById('projects-grid');
    if (!grid) return;

    grid.innerHTML = projects.map((project, index) => {
        // Determine what visual to show: Image or Fallback
        let visualContent;
        
        // Check for valid thumbnail (not null, undefined, or empty string)
        const hasThumbnail = project.thumbnail && project.thumbnail.trim().length > 0;
        
        if (hasThumbnail) {
            visualContent = `
                <img src="${project.thumbnail}" alt="${project.title}" class="w-full h-full object-cover transition-all duration-700 group-hover:scale-105 opacity-80 group-hover:opacity-100 grayscale group-hover:grayscale-0 mix-blend-luminosity group-hover:mix-blend-normal" onerror="this.style.display='none'; this.nextElementSibling.nextElementSibling.style.display='block';">
                <div class="absolute inset-0 bg-midnight/20 group-hover:bg-transparent transition-colors duration-500"></div>
                <!-- Fallback hidden by default, shown on error -->
                <div style="display:none;" class="w-full h-full bg-charcoal relative group-hover:bg-midnight transition-colors duration-500 flex items-center justify-center">
                    <i data-lucide="code-2" class="w-16 h-16 text-fern/40 stroke-1 group-hover:text-terracotta/60 group-hover:scale-110 transition-all duration-500"></i>
                </div>
            `;
        } else {
            // Icon Fallback
            visualContent = `
                <div class="w-full h-full bg-charcoal relative group-hover:bg-midnight transition-colors duration-500 flex items-center justify-center">
                    <i data-lucide="code-2" class="w-16 h-16 text-fern/40 stroke-1 group-hover:text-terracotta/60 group-hover:scale-110 transition-all duration-500"></i>
                </div>
            `;
        }
        
        return `
        <div class="group bg-transparent border border-white/5 hover:border-terracotta/50 transition-all duration-500 fade-in-section cursor-pointer project-card relative overflow-hidden">
            <div class="h-64 overflow-hidden bg-charcoal relative">
                ${visualContent}
                
                <div class="absolute bottom-0 left-0 p-6 w-full z-10">
                    <div class="flex flex-wrap gap-2 mb-3">
                        ${project.tags.slice(0, 3).map(tag => `<span class="text-[10px] font-mono uppercase tracking-widest px-2 py-1 border border-white/10 text-porcelain/60 bg-midnight/80 backdrop-blur-sm">${tag}</span>`).join('')}
                    </div>
                </div>
            </div>
            
            <div class="p-8 border-t border-white/5 bg-midnight relative group-hover:bg-charcoal/30 transition-colors duration-500">
                <h3 class="text-2xl font-serif text-porcelain mb-4 group-hover:text-terracotta transition-colors duration-300">${project.title}</h3>
                <p class="text-fern text-sm font-light leading-relaxed line-clamp-3">${project.description}</p>
                <div class="mt-6 flex items-center text-terracotta text-xs uppercase tracking-widest font-mono group-hover:translate-x-2 transition-transform duration-300">
                    View Case Study <span class="ml-2">&rarr;</span>
                </div>
            </div>
        </div>
        `;
    }).join('');

    grid.querySelectorAll('.project-card').forEach((card, i) => {
        card.addEventListener('click', () => {
             openProjectModal(projects[i]);
        });
    });

    if (typeof initScrollAnimations === 'function') initScrollAnimations();
    if (typeof lucide !== 'undefined') lucide.createIcons();
}

async function openProjectModal(project) {
    const slug = getProjectSlug(project);
    const url = new URL(window.location);
    url.searchParams.set('project', slug);
    history.replaceState(null, '', url.toString());

    let visualHeader;
    
    // Check for valid thumbnail (not null, undefined, or empty string)
    const hasThumbnail = project.thumbnail && project.thumbnail.trim().length > 0;

    if (hasThumbnail) {
        visualHeader = `
             <div class="h-[40vh] w-full overflow-hidden mb-8 border-b border-white/10 relative">
                <img src="${project.thumbnail}" class="w-full h-full object-cover opacity-90 transition-opacity duration-700" onerror="this.style.display='none'; this.nextElementSibling.nextElementSibling.style.display='flex';">
                <div class="absolute inset-0 bg-gradient-to-t from-midnight to-transparent"></div>
                <!-- Fallback hidden by default, shown on error -->
                <div style="display:none;" class="absolute inset-0 bg-charcoal flex items-center justify-center overflow-hidden">
                    <i data-lucide="code-2" class="w-32 h-32 text-fern/20 stroke-1"></i>
                    <div class="absolute inset-0 bg-gradient-to-t from-midnight to-transparent"></div>
                </div>
            </div>
        `;
    } else {
        visualHeader = `
             <div class="h-[40vh] w-full mb-8 border-b border-white/10 relative bg-charcoal flex items-center justify-center overflow-hidden">
                <div class="z-10 flex flex-col items-center justify-center">
                    <i data-lucide="code-2" class="w-32 h-32 text-fern/20 stroke-1 mb-4"></i>
                </div>
                <div class="absolute inset-0 bg-gradient-to-t from-midnight to-transparent"></div>
            </div>
        `;
    }

    let content = `
        <div class="mb-12">
            ${visualHeader}
            <div class="max-w-3xl mx-auto px-6">
                <span class="block text-terracotta text-xs font-mono mb-4 uppercase tracking-widest">Case Study</span>
                <h1 class="text-4xl md:text-5xl font-serif font-light text-porcelain mb-6">${project.title}</h1>
                
                <div class="flex flex-wrap gap-3 mb-12">
                    ${project.tags.map(tag => `<span class="px-3 py-1 border border-white/10 text-fern text-xs font-mono uppercase tracking-widest">${tag}</span>`).join('')}
                </div>
                
                <div class="flex gap-6 mb-12 border-b border-white/10 pb-12">
                    ${(project.links || []).map(link => `
                        <a href="${link.url}" target="_blank" class="flex items-center gap-2 text-porcelain hover:text-terracotta transition-colors font-mono text-xs uppercase tracking-wide border border-white/20 px-4 py-2 hover:border-terracotta">
                            <i data-lucide="${link.icon || 'external-link'}" class="w-4 h-4"></i> ${link.label || 'View Link'}
                        </a>
                    `).join('')}
                </div>
                
                <div class="prose prose-invert prose-lg max-w-none">
                     <p class="text-fern font-light text-lg leading-loose">${project.description}</p>
                </div>
                
                <div id="modal-markdown-content" class="mt-8 prose prose-invert prose-lg max-w-none">
                    <!-- Markdown content loaded here -->
                </div>
            </div>
        </div>
    `;

    if (typeof openModal === 'function') {
        openModal(content);
        if (typeof lucide !== 'undefined') lucide.createIcons();
        
        if (project.markdown) {
             // Check if markdown path is already full path or just filename
             const path = project.markdown.startsWith('content/projects/') ? project.markdown : `content/projects/${project.markdown}`;
             const mdContent = await loadMarkdown(path);
             const markdownContainer = document.getElementById('modal-markdown-content');
             if (markdownContainer && mdContent) {
                 markdownContainer.innerHTML = parseMarkdown(mdContent);
                 if (typeof hljs !== 'undefined') hljs.highlightAll();
                 attachImageLightboxHandlers(markdownContainer);
             }
        }
    }
}

// --- Deep-link Helpers ---

/**
 * Derives a URL-safe slug from a project title.
 *
 * @param {Object} project - Project data object.
 * @returns {string} URL slug.
 */
function getProjectSlug(project) {
    return project.title
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-|-$/g, '');
}

/**
 * Reads the `?project=` URL parameter on page load and auto-opens the
 * matching project modal if a corresponding project is found.
 */
function checkDeepLink() {
    const params = new URLSearchParams(window.location.search);
    const slug = params.get('project');
    if (!slug) return;

    const project = allProjects.find(p => getProjectSlug(p) === slug);
    if (project) openProjectModal(project);
}

/**
 * Attaches close-event listeners to the modal that remove the `?project=`
 * URL parameter from the address bar when the modal is dismissed.
 */
function initProjectModalCloseHook() {
    const clearProjectParam = () => {
        const url = new URL(window.location);
        if (!url.searchParams.has('project')) return;
        url.searchParams.delete('project');
        // Drop the bare '?' left by URLSearchParams when no other params remain.
        const target = url.search && url.search !== '?' ? url.pathname + url.search : url.pathname;
        history.replaceState(null, '', target);
    };

    const closeBtn = document.getElementById('modal-close');
    const overlay  = document.getElementById('modal-overlay');

    if (closeBtn) closeBtn.addEventListener('click', clearProjectParam);
    if (overlay) {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) clearProjectParam();
        });
    }
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') clearProjectParam();
    });
}


