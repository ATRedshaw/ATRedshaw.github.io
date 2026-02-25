// Home Page Logic

document.addEventListener('DOMContentLoaded', async () => {
    const siteData = await loadYamlData('site.yaml');
    if (!siteData) return;

    // Populate Hero Section
    const heroName = document.getElementById('hero-name');
    const heroTitle = document.getElementById('hero-title');
    const heroTagline = document.getElementById('hero-tagline');
    const heroImage = document.getElementById('hero-image');
    const resumeBtn = document.getElementById('resume-btn');

    if (heroName) heroName.textContent = siteData.name;
    if (heroTitle) heroTitle.textContent = siteData.title;
    if (heroTagline) heroTagline.textContent = siteData.tagline;
    if (heroImage && siteData.headshot) {
        heroImage.src = siteData.headshot;
        heroImage.alt = siteData.headshot_alt || siteData.name;
    }
    if (resumeBtn && siteData.resume) {
        resumeBtn.href = siteData.resume;
        resumeBtn.setAttribute('download', '');
    }

    // Populate About Section
    const aboutTextContainer = document.getElementById('about-text');
    if (aboutTextContainer && siteData.about) {
        // Convert newlines to paragraphs
        const paragraphs = siteData.about.split('\n\n').filter(p => p.trim() !== '');
        aboutTextContainer.innerHTML = paragraphs
            .map(p => `<p class="mb-6 text-fern text-lg leading-loose font-light">${p}</p>`)
            .join('');
    }
});
