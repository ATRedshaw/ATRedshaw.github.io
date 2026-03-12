
document.addEventListener('DOMContentLoaded', async () => {
    // Get post ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    const postId = urlParams.get('id');

    if (!postId) {
        window.location.href = 'blog.html';
        return;
    }

    const data = await loadYamlData('blog.yaml');
    if (!data || !data.posts) return;

    // Find the post
    const post = data.posts.find(p => {
        // match based on markdown filename
        const filename = p.markdown.split('/').pop().replace('.md', '');
        return filename === postId;
    });

    if (!post) {
        document.getElementById('blog-post-content').innerHTML = `
            <div class="text-center py-20">
                <h1 class="text-3xl font-serif text-terracotta">Post Not Found</h1>
                <a href="blog.html" class="text-porcelain hover:text-terracotta mt-4 inline-block">Return to Journal</a>
            </div>
        `;
        return;
    }

    renderPost(post);
});

async function renderPost(post) {
    const container = document.getElementById('blog-post-content');
    
    // Set Page Title
    document.title = `${post.title} | Alex Redshaw`;

    const formattedDate = new Date(post.date).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });

    // Tags HTML
    const tagsHtml = post.tags ? post.tags.map(tag => `<span class="px-3 py-1 border border-terracotta/30 text-terracotta text-xs font-mono uppercase tracking-widest">${tag}</span>`).join('') : '';

    // Initial Skeleton / Header
    container.innerHTML = `
        <div class="mb-12 border-b border-white/10 pb-12 fade-in-section">
            <div class="flex flex-wrap gap-3 mb-6">
                ${tagsHtml}
            </div>
            <h1 class="text-4xl md:text-5xl lg:text-6xl font-serif text-porcelain mb-8 leading-tight">${post.title}</h1>
            
            <div class="flex items-center gap-6 text-sm font-mono text-porcelain/40 uppercase tracking-widest">
                <div class="flex items-center gap-2">
                    <i data-lucide="calendar" class="w-4 h-4"></i>
                    <span>${formattedDate}</span>
                </div>
                <span class="text-terracotta">•</span>
                <div class="flex items-center gap-2">
                    <i data-lucide="clock" class="w-4 h-4"></i>
                    <span id="reading-time-display">... read</span>
                </div>
            </div>
        </div>
        
        <!-- Markdown/Prose Content -->
        <article class="prose prose-invert prose-lg max-w-none text-porcelain/70 prose-headings:font-serif prose-headings:text-porcelain prose-headings:font-normal prose-a:text-terracotta prose-a:no-underline hover:prose-a:underline prose-code:text-fern prose-blockquote:border-l-terracotta prose-blockquote:text-porcelain/60 prose-strong:text-porcelain font-light fade-in-section">
            <div id="markdown-content" class="animate-pulse flex flex-col gap-4">
                 <div class="h-4 bg-white/5 w-full rounded"></div>
                 <div class="h-4 bg-white/5 w-full rounded"></div>
                 <div class="h-4 bg-white/5 w-5/6 rounded"></div>
            </div>
        </article>
    `;
    
    // Initialize Icons and Animations for new content
    if (typeof lucide !== 'undefined') lucide.createIcons();
    if (typeof initScrollAnimations === 'function') initScrollAnimations();

    // Fetch Markdown
    if (post.markdown) {
        try {
            const mdText = await loadMarkdown(post.markdown);

            const readingTimeEl = document.getElementById('reading-time-display');
            if (readingTimeEl) readingTimeEl.textContent = `${readingTimeFromChars(mdText.length)} read`;

            const htmlContent = parseMarkdown(mdText);
            const mdContainer = document.getElementById('markdown-content');
            
            if (mdContainer) {
                mdContainer.classList.remove('animate-pulse', 'flex', 'flex-col', 'gap-4');
                mdContainer.innerHTML = htmlContent;
                
                if (typeof hljs !== 'undefined') {
                    mdContainer.querySelectorAll('pre code').forEach((block) => {
                        hljs.highlightElement(block);
                    });
                }

                attachImageLightboxHandlers(mdContainer);
            }
        } catch (e) {
            console.error('Error loading markdown:', e);
            const mdContainer = document.getElementById('markdown-content');
            if(mdContainer) mdContainer.innerHTML = "<p>Error loading content.</p>";
        }
    }
}
