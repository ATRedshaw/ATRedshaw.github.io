function initNavbar() {
    const button = document.getElementById('mobile-menu-btn');
    const menu = document.getElementById('mobile-menu');
    button.addEventListener('click', () => {
        const expanded = button.getAttribute('aria-expanded') !== 'true';
        button.setAttribute('aria-expanded', String(expanded));
        button.setAttribute('aria-label', expanded ? 'Close navigation' : 'Open navigation');
        menu.classList.toggle('hidden', !expanded);
    });
}

function initScrollAnimations() {
    if (!('IntersectionObserver' in window) || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0 });

    document.querySelectorAll('.fade-in-section').forEach(section => {
        section.classList.add('will-animate');
        observer.observe(section);
    });
}

function initFilters() {
    const controls = document.querySelector('[data-filter-controls]');
    if (!controls) return;

    const cards = document.querySelectorAll('[data-filter-grid] > [data-tags]');
    controls.hidden = false;
    controls.querySelector('select').addEventListener('change', event => {
        cards.forEach(card => {
            card.hidden = event.target.value !== 'all' && !JSON.parse(card.dataset.tags).includes(event.target.value);
        });
    });
}

function redirectLegacyLink() {
    const parameters = new URLSearchParams(window.location.search);
    const postId = parameters.get('id');
    const projectSlug = parameters.get('project');
    // Match only generated local links, keeping old shared URLs working.
    const link = Array.from(document.querySelectorAll('[data-legacy-id], [data-legacy-slug]')).find(element =>
        (postId && element.dataset.legacyId === postId) ||
        (projectSlug && element.dataset.legacySlug === projectSlug)
    );
    if (link) {
        const target = link.matches('a') ? link : link.querySelector('a');
        window.location.replace(target.getAttribute('href') + window.location.hash);
    }
}

function initArticle() {
    const article = document.querySelector('[data-article-body]');
    if (!article) return;

    if (typeof hljs !== 'undefined') {
        article.querySelectorAll('pre code').forEach(block => hljs.highlightElement(block));
    }
    if (typeof katex !== 'undefined') {
        article.querySelectorAll('.arithmatex').forEach(element => {
            katex.render(element.textContent.slice(2, -2), element, {
                displayMode: element.tagName === 'DIV',
                throwOnError: false,
            });
        });
    }
    article.querySelectorAll('img').forEach(img => {
        img.classList.add('prose-img-zoomable');
        img.tabIndex = 0;
        img.setAttribute('role', 'button');
        img.setAttribute('aria-label', `Enlarge image: ${img.alt}`);
        img.addEventListener('click', () => openLightbox(img));
        img.addEventListener('keydown', event => {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                openLightbox(img);
            }
        });
    });
}

let lightboxTrigger;

function openLightbox(trigger) {
    let lightbox = document.getElementById('img-lightbox');
    if (!lightbox) {
        lightbox = document.createElement('dialog');
        lightbox.id = 'img-lightbox';
        lightbox.setAttribute('aria-label', 'Image viewer');
        lightbox.innerHTML = `
            <img class="img-lightbox__img" alt="">
            <button class="img-lightbox__close" aria-label="Close image">&times;</button>
        `;
        document.body.appendChild(lightbox);
        lightbox.addEventListener('click', event => {
            if (event.target === lightbox || event.target.closest('button')) lightbox.close();
        });
        lightbox.addEventListener('close', () => {
            lightbox.classList.remove('img-lightbox--active');
            document.body.style.overflow = '';
            lightboxTrigger.focus();
        });
    }
    lightboxTrigger = trigger;
    const image = lightbox.querySelector('img');
    image.src = trigger.src;
    image.alt = trigger.alt;
    lightbox.showModal();
    lightbox.classList.add('img-lightbox--active');
    document.body.style.overflow = 'hidden';
}

document.addEventListener('DOMContentLoaded', () => {
    redirectLegacyLink();
    initNavbar();
    initFilters();
    initArticle();
    initScrollAnimations();
    if (typeof lucide !== 'undefined') lucide.createIcons();
});
