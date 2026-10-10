module.exports = {
    theme: {
        extend: {
            fontFamily: {
                sans: ['Montserrat', 'sans-serif'],
                serif: ['Fraunces', 'serif'],
                mono: ['Space Mono', 'monospace'],
            },
            colors: {
                matcha: '#E0E1DD',
                midnight: '#0D1B2A',
                charcoal: '#1B263B',
                fern: '#415A77',
                cream: '#F4F1EA',
                porcelain: '#E0E1DD',
                terracotta: '#E07A5F',
                surface: '#0D1B2A',
                'surface-light': '#1B263B',
                text: '#F4F1EA',
                muted: '#778DA9',
                accent: '#E07A5F',
            },
            backgroundImage: {
                grain: "url('data:image/svg+xml,%3Csvg viewBox=\"0 0 200 200\" xmlns=\"http://www.w3.org/2000/svg\"%3E%3Cfilter id=\"noiseFilter\"%3E%3CfeTurbulence type=\"fractalNoise\" baseFrequency=\"0.65\" numOctaves=\"3\" stitchTiles=\"stitch\"/%3E%3C/filter%3E%3Crect width=\"100%25\" height=\"100%25\" filter=\"url(%23noiseFilter)\" opacity=\"0.05\"/%3E%3C/svg%3E')",
            },
        },
    },
};
