// Blog Page Logic

let allPosts = [];

document.addEventListener('DOMContentLoaded', async () => {
    const data = await loadYamlData('blog.yaml');
    if (!data || !data.posts) return;

    // Sort by date descending
    allPosts = data.posts.sort((a, b) => new Date(b.date) - new Date(a.date));
    
    setupBlogFilters();
    renderBlogPosts(allPosts);
    
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
});

function setupBlogFilters() {
    const filterContainer = document.getElementById('blog-filter-container');
    if (!filterContainer) return;

    const tags = new Set();
    allPosts.forEach(p => p.tags.forEach(t => tags.add(t)));
    
    let html = `<button class="blog-filter-btn active px-4 py-2 rounded-full text-sm font-medium bg-slate-800 text-white transition-all shadow-sm hover:bg-slate-700" data-filter="all">All</button>`;
    
    tags.forEach(tag => {
        html += `<button class="blog-filter-btn px-4 py-2 rounded-full text-sm font-medium bg-white text-slate-600 border border-slate-200 transition-all shadow-sm hover:bg-slate-50 hover:text-blue-600" data-filter="${tag}">${tag}</button>`;
    });

    filterContainer.innerHTML = html;

    filterContainer.querySelectorAll('.blog-filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.blog-filter-btn').forEach(b => {
                b.classList.remove('bg-slate-800', 'text-white');
                b.classList.add('bg-white', 'text-slate-600', 'border', 'border-slate-200');
            });
            e.target.classList.remove('bg-white', 'text-slate-600', 'border', 'border-slate-200');
            e.target.classList.add('bg-slate-800', 'text-white');

            const filterValue = e.target.getAttribute('data-filter');
            filterPosts(filterValue);
        });
    });
}

function filterPosts(filter) {
    if (filter === 'all') {
        renderBlogPosts(allPosts);
    } else {
        const filtered = allPosts.filter(p => p.tags.includes(filter));
        renderBlogPosts(filtered);
    }
}

function renderBlogPosts(posts) {
    const grid = document.getElementById('blog-grid');
    if (!grid) return;

    grid.innerHTML = posts.map((post, index) => {
        return `
        <article class="bg-white p-8 rounded-xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow cursor-pointer fade-in-section blog-card flex flex-col justify-between h-full" data-index="${index}">
            <div>
                <div class="flex items-center gap-4 text-xs text-slate-400 mb-4">
                    <span class="flex items-center gap-1">
                        <i data-lucide="calendar" class="w-3 h-3"></i> ${new Date(post.date).toLocaleDateString()}
                    </span>
                    <span class="flex items-center gap-1">
                        <i data-lucide="clock" class="w-3 h-3"></i> ${post.reading_time || '5 min'} read
                    </span>
                </div>
                
                <h2 class="text-2xl font-bold text-slate-800 mb-3 hover:text-blue-600 transition-colors">${post.title}</h2>
                <p class="text-slate-600 leading-relaxed mb-6">${post.excerpt}</p>
            </div>
            
            <div class="flex items-center justify-between mt-auto">
                <div class="flex gap-2">
                    ${post.tags.map(tag => `<span class="text-xs font-medium px-2 py-1 rounded bg-slate-100 text-slate-600">${tag}</span>`).slice(0, 2).join('')}
                </div>
                <span class="text-blue-600 text-sm font-semibold flex items-center gap-1 group">
                    Read Post <i data-lucide="arrow-right" class="w-4 h-4 transition-transform group-hover:translate-x-1"></i>
                </span>
            </div>
        </article>
        `;
    }).join('');

    grid.querySelectorAll('.blog-card').forEach((card, i) => {
        card.addEventListener('click', () => {
             openBlogModal(posts[i]);
        });
    });

    if (typeof lucide !== 'undefined') lucide.createIcons();
    initScrollAnimations();
}

async function openBlogModal(post) {
    let content = `
        <div class="mb-8 border-b border-slate-100 pb-8">
            <div class="flex gap-2 mb-4">
                ${post.tags.map(tag => `<span class="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-xs font-bold uppercase tracking-wide">${tag}</span>`).join('')}
            </div>
            <h1 class="text-3xl md:text-4xl font-extrabold text-slate-900 mb-4 leading-tight">${post.title}</h1>
            <div class="flex items-center gap-4 text-sm text-slate-500">
                <span>${new Date(post.date).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</span>
                <span>&bull;</span>
                <span>${post.reading_time} read</span>
            </div>
        </div>
        <div class="prose prose-lg max-w-none text-slate-600">
            <div id="modal-markdown-content" class="animate-pulse">Loading content...</div>
        </div>
    `;

    openModal(content);

     // Fetch Markdown
    if (post.markdown) {
        const mdText = await loadMarkdown(post.markdown);
        const htmlContent = marked.parse(mdText);
        const container = document.getElementById('modal-markdown-content');
        if (container) {
            container.classList.remove('animate-pulse');
            container.innerHTML = htmlContent;
             if (typeof hljs !== 'undefined') {
                 container.querySelectorAll('pre code').forEach((block) => {
                    hljs.highlightElement(block);
                });
            }
        }
    }
}
