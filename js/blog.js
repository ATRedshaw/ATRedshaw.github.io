// Blog Page Logic: Filtering & Rendering

let allPosts = [];

document.addEventListener('DOMContentLoaded', async () => {
    const data = await loadYamlData('blog.yaml');
    if (!data || !data.posts) return;

    // Sort by date descending
    allPosts = data.posts.sort((a, b) => new Date(b.date) - new Date(a.date));

    // Compute reading times from markdown character counts
    await Promise.all(allPosts.map(async post => {
        try {
            const text = await loadMarkdown(post.markdown);
            post.reading_time = readingTimeFromChars(text.length);
        } catch {
            post.reading_time = '1 min';
        }
    }));
    
    setupBlogFilters();
    renderBlogPosts(allPosts);
    
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
});

function setupBlogFilters() {
    const filterContainer = document.getElementById('blog-filter-container');
    if (!filterContainer) return;

    const tagsSet = new Set();
    allPosts.forEach(p => p.tags.forEach(t => tagsSet.add(t)));
    const tags = Array.from(tagsSet).sort();
    
    // Create Dropdown (Minimalist Design)
    const select = document.createElement('select');
    select.className = 'bg-midnight text-porcelain border border-white/10 px-6 py-3 font-mono text-xs uppercase tracking-widest focus:outline-none focus:border-terracotta transition-colors cursor-pointer appearance-none pr-10 relative z-10';
    select.style.backgroundImage = 'url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'16\' height=\'16\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'%23F4F1EA\' stroke-width=\'2\' stroke-linecap=\'round\' stroke-linejoin=\'round\'%3E%3Cpolyline points=\'6 9 12 15 18 9\'%3E%3C/polyline%3E%3C/svg%3E")';
    select.style.backgroundRepeat = 'no-repeat';
    select.style.backgroundPosition = 'right 1rem center';
    
    let optionsHtml = `<option value="all">All Topics</option>`;
    
    tags.forEach(tag => {
        optionsHtml += `<option value="${tag}">${tag}</option>`;
    });

    select.innerHTML = optionsHtml;
    filterContainer.innerHTML = '';
    filterContainer.appendChild(select);

    select.addEventListener('change', (e) => {
        const filterValue = e.target.value;
        const grid = document.getElementById('blog-grid');
        if(grid) {
            grid.style.opacity = '0';
            setTimeout(() => {
                filterPosts(filterValue);
                // grid.style.opacity = '1'; // Handled in filterPosts or by render?
                // actually filterPosts already does the opacity transition, let's just call it.
                // Wait, filterPosts implementation in file handles opacity.
            }, 0); 
        } else {
             filterPosts(filterValue);
        }
    });
}

function filterPosts(filter) {
    const grid = document.getElementById('blog-grid');
    if(grid) {
        grid.style.opacity = '0';
        setTimeout(() => {
            if (filter === 'all') {
                renderBlogPosts(allPosts);
            } else {
                const filtered = allPosts.filter(p => p.tags.includes(filter));
                renderBlogPosts(filtered);
            }
            grid.style.opacity = '1';
        }, 300);
    }
}

function renderBlogPosts(posts) {
    const grid = document.getElementById('blog-grid');
    if (!grid) return;

    grid.innerHTML = posts.map((post, index) => {
        const dateObj = new Date(post.date);
        const dateStr = dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
        
        return `
        <article class="group relative border-t border-white/5 py-12 md:py-16 transition-colors duration-500 hover:bg-white/[0.02] cursor-pointer blog-card fade-in-section" data-index="${index}">
            <div class="flex flex-col md:flex-row md:items-baseline gap-6 md:gap-12">
                
                <!-- Date -->
                <div class="md:w-1/6 flex flex-col md:items-end flex-shrink-0">
                    <span class="font-mono text-terracotta text-sm tracking-widest uppercase mb-2">${dateStr}</span>
                     <span class="font-mono text-[10px] text-fern/60 uppercase tracking-widest border border-white/5 px-2 py-0.5 inline-block md:hidden w-fit">
                        ${post.reading_time || '5 min'} read
                    </span>
                </div>

                <!-- Content -->
                <div class="md:w-4/6">
                    <h2 class="text-3xl font-serif text-porcelain mb-4 group-hover:text-terracotta transition-colors duration-300">
                        ${post.title}
                    </h2>
                    <p class="text-fern font-light leading-relaxed mb-6 max-w-2xl">
                        ${post.excerpt}
                    </p>
                    <div class="flex flex-wrap gap-2 text-fern text-xs uppercase tracking-widest font-medium mt-4">
                         ${post.tags.map(tag => `
                            <span>${tag}</span>
                        `).join('<span class="text-white/20 px-1">&bull;</span>')}
                    </div>
                </div>

                <!-- Meta (Right Side Desktop) -->
                <div class="hidden md:flex md:w-1/6 flex-col items-end gap-3 opacity-60 group-hover:opacity-100 transition-opacity duration-500">
                    <span class="font-mono text-xs text-fern uppercase tracking-widest">
                        ${post.reading_time || '5 min'} read
                    </span>
                 </div>

            </div>
        </article>
        `;
    }).join('');

    // Add click listeners
    const cards = grid.querySelectorAll('.blog-card');
    cards.forEach((card, i) => {
        card.addEventListener('click', () => {
             const filename = posts[i].markdown.split('/').pop().replace('.md', '');
             window.location.href = `post.html?id=${filename}`;
        });
    });

    if (typeof lucide !== 'undefined') lucide.createIcons();
    if (typeof initScrollAnimations === 'function') initScrollAnimations();
}

