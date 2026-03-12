// Experience Page Logic: Skills & Timeline

document.addEventListener('DOMContentLoaded', async () => {
    await loadSkills();
    await loadExperience();
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
});

async function loadSkills() {
    const data = await loadYamlData('skills.yaml');
    if (!data || !data.categories) return;

    const skillsContainer = document.getElementById('skills-container');
    if (!skillsContainer) return;

    skillsContainer.innerHTML = data.categories.map(category => `
        <div class="bg-charcoal/20 p-8 border border-white/5 fade-in-section hover:border-terracotta/30 transition-colors duration-500">
            <h3 class="text-xl font-serif text-terracotta mb-6 flex items-center gap-2">
                ${category.name}
            </h3>
            <div class="flex flex-wrap gap-2">
                ${category.skills.map(skill => `
                    <span class="px-3 py-1.5 border border-white/10 text-porcelain/70 text-xs font-mono tracking-wide hover:border-terracotta hover:text-terracotta transition-colors duration-300">
                        ${skill}
                    </span>
                `).join('')}
            </div>
        </div>
    `).join('');
    
    // Re-run animation observer for new elements
    if (typeof initScrollAnimations === 'function') initScrollAnimations();
}

async function loadExperience() {
    const data = await loadYamlData('experience.yaml');
    if (!data || !data.entries) return;

    const timelineContainer = document.getElementById('timeline-container');
    const certificationsContainer = document.getElementById('certifications-container');

    // Filter entries
    const timelineEntries = data.entries.filter(entry => entry.type !== 'certification');
    const certificationEntries = data.entries.filter(entry => entry.type === 'certification');

    // 1. Render Timeline
    if (timelineContainer) {
        timelineContainer.innerHTML = timelineEntries.map((entry, index) => {
            // Determine alignment classes based on index (even/odd)
            // Even: Right side (md screen), Odd: Left side (md screen)
            // Actually, usually in centered vertical timelines:
            // Odd indices = Left, Even indices = Right is standard or vice versa.
            // Let's go with: Index 0 (latest) -> Left ... no wait, let's alternate.
            
            const isLeft = index % 2 === 0;
            const containerClass = isLeft ? 'md:flex-row' : 'md:flex-row-reverse';
            const textAlignClass = isLeft ? 'md:text-right' : 'md:text-left';
            const itemsAlignClass = isLeft ? 'md:items-end' : 'md:items-start';
            const marginClass = isLeft ? 'md:pr-12' : 'md:pl-12';
            
            // Icon logic
            let iconName = 'briefcase';
            if (entry.type === 'education') iconName = 'graduation-cap';

            return `
            <div class="relative flex flex-col ${containerClass} md:items-center group fade-in-section">
                
                <!-- Dot on Line -->
                <div class="absolute left-[-29px] md:left-1/2 md:-ml-[5px] top-6 w-[10px] h-[10px] bg-terracotta rounded-full z-10 ring-4 ring-midnight"></div>
                
                <!-- Date (Opposite side on desktop) -->
                <div class="hidden md:flex md:w-1/2 ${isLeft ? 'justify-start pl-12' : 'justify-end pr-12'} order-1 md:order-none mb-2 md:mb-0">
                   <div class="flex flex-col ${isLeft ? 'items-start' : 'items-end'}">
                        <span class="text-sm font-mono text-terracotta tracking-widest uppercase mb-1">${entry.date}</span>
                        <span class="text-[10px] font-mono text-fern/50 uppercase tracking-widest border border-white/5 px-2 py-0.5">${entry.type}</span>
                   </div>
                </div>

                <!-- Content Card -->
                <div class="md:w-1/2 ${marginClass} mb-8 md:mb-0 w-full relative">
                    <!-- Mobile Date -->
                    <div class="md:hidden flex items-center gap-3 mb-3 pl-2">
                        <span class="text-xs font-mono text-terracotta tracking-widest uppercase">${entry.date}</span>
                        <span class="text-[10px] font-mono text-fern/50 uppercase tracking-widest border border-white/5 px-2 py-0.5">${entry.type}</span>
                    </div>

                    <div class="bg-transparent border border-white/5 p-8 transition-all duration-500 hover:border-terracotta/30 hover:bg-white/[0.02]">
                        <h3 class="text-xl font-serif text-porcelain mb-1">${entry.title}</h3>
                        <div class="text-fern text-sm font-mono mb-4 uppercase tracking-wide">${entry.organization}</div>
                        <p class="text-porcelain/60 leading-loose font-light text-sm">
                            ${entry.description}
                        </p>
                    </div>
                </div>
            </div>
            `;
        }).join('');
    }

    // 2. Render Certifications
    if (certificationsContainer) {
        certificationsContainer.innerHTML = certificationEntries.map(cert => `
            <div class="bg-transparent p-6 border border-white/5 flex items-start gap-4 hover:border-terracotta/30 transition-colors duration-300">
                <div class="flex-shrink-0 w-10 h-10 border border-white/10 text-terracotta flex items-center justify-center rounded-none">
                    <i data-lucide="award" class="w-5 h-5"></i>
                </div>
                <div>
                    <h4 class="font-serif text-porcelain text-lg mb-1">${cert.title}</h4>
                    <p class="text-xs font-mono text-fern uppercase tracking-widest mb-3">${cert.organization} <span class="mx-1 text-terracotta">•</span> ${cert.date}</p>
                    <p class="text-sm text-porcelain/60 font-light leading-relaxed">${cert.description}</p>
                </div>
            </div>
        `).join('');
    }

    if (typeof lucide !== 'undefined') lucide.createIcons();
    if (typeof initScrollAnimations === 'function') initScrollAnimations();
}
