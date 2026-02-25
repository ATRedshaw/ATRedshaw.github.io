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
});

function setupFilters() {
    const filterContainer = document.getElementById('filter-container');
    if (!filterContainer) return;

    // Extract unique tags
    const tags = new Set();
    allProjects.forEach(p => p.tags.forEach(t => tags.add(t)));
    
    // Create Buttons
    let html = `<button class="filter-btn active px-4 py-2 rounded-full text-sm font-medium bg-slate-800 text-white transition-all shadow-sm hover:bg-slate-700" data-filter="all">All</button>`;
    
    tags.forEach(tag => {
        html += `<button class="filter-btn px-4 py-2 rounded-full text-sm font-medium bg-white text-slate-600 border border-slate-200 transition-all shadow-sm hover:bg-slate-50 hover:text-blue-600" data-filter="${tag}">${tag}</button>`;
    });

    filterContainer.innerHTML = html;

    // Add Event Listeners
    filterContainer.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            // Update UI
            document.querySelectorAll('.filter-btn').forEach(b => {
                b.classList.remove('bg-slate-800', 'text-white');
                b.classList.add('bg-white', 'text-slate-600', 'border', 'border-slate-200');
            });
            e.target.classList.remove('bg-white', 'text-slate-600', 'border', 'border-slate-200');
            e.target.classList.add('bg-slate-800', 'text-white');

            const filterValue = e.target.getAttribute('data-filter');
            filterProjects(filterValue);
        });
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
        const imageSrc = project.thumbnail || 'https://via.placeholder.com/600x400?text=No+Image';
        
        return `
        <div class="group bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 fade-in-section cursor-pointer project-card" data-index="${index}">
            <div class="h-48 overflow-hidden bg-slate-100 relative">
                <img src="${imageSrc}" alt="${project.title}" class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105">
                <div class="absolute inset-0 bg-gradient-to-t from-slate-900/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end p-4">
                     <span class="text-white text-sm font-medium">View Details &rarr;</span>
                </div>
            </div>
            <div class="p-6">
                <div class="flex flex-wrap gap-2 mb-3">
                    ${project.tags.map(tag => `<span class="text-xs font-medium px-2.5 py-0.5 rounded bg-blue-50 text-blue-600">${tag}</span>`).slice(0, 3).join('')}
                    ${project.tags.length > 3 ? `<span class="text-xs font-medium px-2.5 py-0.5 rounded bg-slate-50 text-slate-500">+${project.tags.length - 3}</span>` : ''}
                </div>
                <h3 class="text-xl font-bold text-slate-800 mb-2 group-hover:text-blue-600 transition-colors">${project.title}</h3>
                <p class="text-slate-600 text-sm line-clamp-2">${project.description}</p>
            </div>
        </div>
        `;
    }).join('');

    // Re-bind click events for modals handles
    // Note: We need to find the correct project object relative to the rendered list, 
    // but the data-index above refers to the index in the CURRENT filtered array or the original?
    // Let's use the title or a unique ID if possible. Using title for simplicity in this static context.
    
    grid.querySelectorAll('.project-card').forEach((card, i) => {
        card.addEventListener('click', () => {
             // 'projects' here is the currently rendered array (filtered or all)
             // 'i' matches the index in the loop above
             openProjectModal(projects[i]);
        });
    });

    initScrollAnimations();
}

async function openProjectModal(project) {
    let content = `
        <div class="mb-6">
             <div class="h-64 w-full rounded-xl overflow-hidden mb-6 bg-slate-100">
                <img src="${project.thumbnail || ''}" class="w-full h-full object-cover">
            </div>
            <h1 class="text-3xl font-bold text-slate-900 mb-2">${project.title}</h1>
            <div class="flex flex-wrap gap-2 mb-4">
                ${project.tags.map(tag => `<span class="px-3 py-1 bg-slate-100 text-slate-600 rounded-full text-sm">${tag}</span>`).join('')}
            </div>
            
            <div class="flex gap-4 mb-8">
                ${project.links && project.links.github ? `
                    <a href="${project.links.github}" target="_blank" class="flex items-center gap-2 text-slate-700 hover:text-blue-600 font-medium">
                        <i data-lucide="github" class="w-5 h-5"></i> View Code
                    </a>
                ` : ''}
                 ${project.links && project.links.demo ? `
                    <a href="${project.links.demo}" target="_blank" class="flex items-center gap-2 text-slate-700 hover:text-blue-600 font-medium">
                        <i data-lucide="external-link" class="w-5 h-5"></i> Live Demo
                    </a>
                ` : ''}
            </div>
        </div>
        <div class="prose max-w-none text-slate-600">
            <!-- Markdown content will be injected here -->
            <div id="modal-markdown-content" class="animate-pulse">Loading content...</div>
        </div>
    `;

    openModal(content);
    if (typeof lucide !== 'undefined') lucide.createIcons();

    // Fetch Markdown
    if (project.markdown) {
        const mdText = await loadMarkdown(project.markdown);
        const htmlContent = marked.parse(mdText);
        const container = document.getElementById('modal-markdown-content');
        if (container) {
            container.classList.remove('animate-pulse');
            container.innerHTML = htmlContent;
            // Highlight code blocks
            if (typeof hljs !== 'undefined') {
                 container.querySelectorAll('pre code').forEach((block) => {
                    hljs.highlightElement(block);
                });
            }
        }
    } else {
        document.getElementById('modal-markdown-content').innerHTML = "<p>No detailed content available.</p>";
    }
}
