/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./epc/*.html",
    "./epc/*.js",
    "./components/**/*.{js,jsx}",
    "./*.html"
  ],
  theme: {
    extend: {
      // Saber Brand Colors
      colors: {
        // Primary Brand Colours
        'saber-blue': '#044D73',
        'saber-green': '#7CC061',
        
        // Secondary Colours
        'saber-dark-blue': '#091922',
        'saber-dark-green': '#0A2515',
        'saber-gradient-dark': '#0d1138',
        
        // Operational UI Colours
        'ops-surface': '#F8FAFB',
        'ops-surface-dark': '#1A1F2E',
        'ops-border': '#E1E8ED',
        'ops-border-dark': '#2D3748',
        
        // Status Colours
        'status-success': '#10B981',
        'status-warning': '#F59E0B',
        'status-error': '#EF4444',
        'status-info': '#3B82F6',
        'status-pending': '#8B5CF6',
        
        // Text Hierarchy
        'text-primary': '#091922',
        'text-secondary': '#4B5563',
        'text-tertiary': '#9CA3AF',
        'text-inverse': '#FFFFFF',

        // Shadow colors for better effects
        'shadow-green': 'rgba(124, 192, 97, 0.2)',
        'shadow-blue': 'rgba(4, 77, 115, 0.2)',
      },
      
      // Typography System
      fontFamily: {
        'heading': ['Montserrat', 'system-ui', 'sans-serif'],
        'body': ['Inter', 'system-ui', 'sans-serif'],
        'mono': ['JetBrains Mono', 'monospace'],
      },
      
      fontSize: {
        // Heading Sizes
        'h1': ['2.5rem', { lineHeight: '2.875rem', fontWeight: '800' }],
        'h2': ['2rem', { lineHeight: '2.375rem', fontWeight: '700' }],
        'h3': ['1.75rem', { lineHeight: '2.125rem', fontWeight: '600' }],
        'h4': ['1.5rem', { lineHeight: '1.875rem', fontWeight: '600' }],
        'h5': ['1.25rem', { lineHeight: '1.625rem', fontWeight: '500' }],
        'h6': ['1.125rem', { lineHeight: '1.5rem', fontWeight: '500' }],
        
        // Body Sizes
        'body-lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'body': ['1rem', { lineHeight: '1.5rem' }],
        'body-sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'caption': ['0.75rem', { lineHeight: '1rem' }],
      },
      
      // Logo Sizing System
      width: {
        'logo-xs': '100px',   // Minimum size
        'logo-sm': '140px',   // Mobile logo
        'logo-md': '180px',   // Default logo
        'logo-lg': '220px',   // Desktop logo
        'logo-xl': '280px',   // Hero sections
      },
      height: {
        'logo-xs': '28px',
        'logo-sm': '40px',
        'logo-md': '51px',
        'logo-lg': '62px',
        'logo-xl': '79px',
      },
      
      // Consistent Spacing Scale
      spacing: {
        'xs': '0.25rem',   // 4px
        'sm': '0.5rem',    // 8px
        'md': '1rem',      // 16px
        'lg': '1.5rem',    // 24px
        'xl': '2rem',      // 32px
        '2xl': '3rem',     // 48px
        '3xl': '4rem',     // 64px
        'section': '5rem', // 80px
      },
      
      // Background Gradients
      backgroundImage: {
        'gradient-brand': 'linear-gradient(135deg, #044D73 0%, #7CC061 100%)',
        'gradient-energy': 'linear-gradient(135deg, #7CC061 0%, #044D73 100%)',
        'gradient-dark': 'linear-gradient(135deg, #091922 0%, #0d1138 100%)',
        'gradient-mesh': 'radial-gradient(circle at 50% 50%, #7CC061 0%, transparent 50%)',
        'gradient-glow': 'radial-gradient(circle at 50% 50%, #044D73 0%, transparent 70%)',
      },
      
      // Animation and Transitions
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 3s ease-in-out infinite',
      },
      
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        }
      },
      
      // Box Shadows
      boxShadow: {
        'brand': '0 4px 14px 0 rgba(4, 77, 115, 0.15)',
        'brand-lg': '0 10px 40px 0 rgba(4, 77, 115, 0.15)',
        'energy': '0 4px 14px 0 rgba(124, 192, 97, 0.15)',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}