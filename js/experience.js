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
        <div class="bg-white p-6 rounded-lg shadow-sm border border-slate-100 fade-in-section">
            <h3 class="text-xl font-semibold text-slate-800 mb-4">${category.name}</h3>
            <div class="flex flex-wrap gap-2">
                ${category.skills.map(skill => `
                    <span class="px-3 py-1 bg-slate-100 text-slate-700 rounded-full text-sm font-medium hover:bg-blue-50 hover:text-blue-600 transition-colors">
                        ${skill}
                    </span>
                `).join('')}
            </div>
        </div>
    `).join('');
    
    // Re-run animation observer for new elements
    initScrollAnimations();
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
            // Determine icon and color based on type
            let iconName = 'briefcase';
            let colorClass = 'bg-blue-100 text-blue-600';
            
            if (entry.type === 'education') {
                iconName = 'graduation-cap';
                colorClass = 'bg-emerald-100 text-emerald-600';
            }

            return `
            <div class="relative pl-8 sm:pl-32 py-6 group fade-in-section">
                <!-- Timeline Line (Visual) -->
                <div class="hidden sm:flex flex-col items-end absolute left-0 top-6 w-24 pr-4">
                    <span class="text-sm font-semibold text-slate-500 text-right">${entry.date}</span>
                    <span class="text-xs text-slate-400 capitalize mt-1 border border-slate-200 px-2 py-0.5 rounded-full">${entry.type}</span>
                </div>
                
                <!-- Mobile Date (visible only on small screens) -->
                <div class="sm:hidden mb-1 flex items-center gap-2">
                    <span class="text-sm font-bold text-slate-600">${entry.date}</span>
                    <span class="text-xs text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full capitalize">${entry.type}</span>
                </div>

                <!-- Icon Indicator -->
                <div class="absolute left-0 sm:left-[7.5rem] top-6 w-8 h-8 rounded-full ${colorClass} flex items-center justify-center z-10 border-2 border-white shadow-sm">
                    <i data-lucide="${iconName}" class="w-4 h-4"></i>
                </div>
                
                <!-- Content Card -->
                <div class="bg-white p-5 rounded-lg border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
                    <h3 class="text-lg font-bold text-slate-800">${entry.title}</h3>
                    <div class="text-blue-600 font-medium mb-2">${entry.organization}</div>
                    <p class="text-slate-600 leading-relaxed text-sm">
                        ${entry.description}
                    </p>
                </div>
            </div>
            `;
        }).join('');
    }

    // 2. Render Certifications
    if (certificationsContainer) {
        certificationsContainer.innerHTML = certificationEntries.map(cert => `
            <div class="bg-white p-4 rounded-lg border border-slate-100 shadow-sm flex items-start gap-4 hover:border-amber-200 transition-colors">
                <div class="flex-shrink-0 w-10 h-10 bg-amber-50 text-amber-600 rounded-full flex items-center justify-center">
                    <i data-lucide="award" class="w-5 h-5"></i>
                </div>
                <div>
                    <h4 class="font-bold text-slate-800">${cert.title}</h4>
                    <p class="text-sm text-slate-500 mb-1">${cert.organization} &bull; ${cert.date}</p>
                    <p class="text-xs text-slate-600">${cert.description}</p>
                </div>
            </div>
        `).join('');
    }
    
    // Re-run animation observer for new elements
    initScrollAnimations();
}
