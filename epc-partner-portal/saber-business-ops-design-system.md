### Logo System & Official Usage

```javascript
// Logo Configuration for Tailwind
module.exports = {
  theme: {
    extend: {
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
      }
    }
  }
}
```

### Official Saber Logo Structure
The Saber logo consists of:
- **Infinity Symbol**: Interlocking blue (#044D73) and green (#7CC061) curves
- **Wordmark**: "SABER" in bold, "RENEWABLE ENERGY" in lighter weight
- **Clear Space**: Minimum space equal to the height of the "S" in SABER

### Logo Implementation

```jsx
// components/brand/SaberLogo.jsx
const SaberLogo = ({ 
  variant = 'primary',     // primary | white | mono-blue | mono-green | symbol-only
  layout = 'horizontal',   // horizontal | stacked | compact
  size = 'md',            // xs | sm | md | lg | xl
  className = '' 
}) => {
  // Logo paths based on actual Saber branding
  const logoSrc = {
    primary: {
      horizontal: '/assets/logos/saber-logo-horizontal.svg',
      stacked: '/assets/logos/saber-logo-stacked.svg',
      compact: '/assets/logos/saber-logo-compact.svg', // Symbol + SABER only
    },
    white: {
      horizontal: '/assets/logos/saber-logo-horizontal-white.svg',
      stacked: '/assets/logos/saber-logo-stacked-white.svg',
      compact: '/assets/logos/saber-logo-compact-white.svg',
    },
    'mono-blue': {
      horizontal: '/assets/logos/saber-logo-horizontal-mono-blue.svg',
      stacked: '/assets/logos/saber-logo-stacked-mono-blue.svg',
      compact: '/assets/logos/saber-logo-compact-mono-blue.svg',
    },
    'mono-green': {
      horizontal: '/assets/logos/saber-logo-horizontal-mono-green.svg',
      stacked: '/assets/logos/saber-logo-stacked-mono-green.svg',
      compact: '/assets/logos/saber-logo-compact-mono-green.svg',
    },
    'symbol-only': {
      horizontal: '/assets/logos/saber-symbol.svg',
      stacked: '/assets/logos/saber-symbol.svg',
      compact: '/assets/logos/saber-symbol.svg',
    }
  }
  
  const sizes = {
    xs: 'w-logo-xs h-logo-xs',
    sm: 'w-logo-sm h-logo-sm',
    md: 'w-logo-md h-logo-md',
    lg: 'w-logo-lg h-logo-lg',
    xl: 'w-logo-xl h-logo-xl',
  }
  
  // Aspect ratio classes for proper scaling
  const aspectRatios = {
    horizontal: 'aspect-[3.53/1]',  // Standard horizontal ratio
    stacked: 'aspect-[1.8/1]',      // Stacked version ratio
    compact: 'aspect-[2.5/1]',      // Compact version ratio
    'symbol-only': 'aspect-square', // Symbol is square
  }
  
  return (
    <div className={`inline-flex items-center ${className}`}>
      <img 
        src={logoSrc[variant][layout]}
        alt="Saber Renewable Energy"
        className={`${sizes[size]} ${aspectRatios[layout]} object-contain`}
      />
    </div>
  )
}
```

### Business Ops Platform Logo Usage

```jsx
// EPC Portal Header - Current Implementation Style
const EPCPortalHeader = () => (
  <header className="bg-white shadow-sm">
    <div className="border-b-2 border-saber-green/20">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo Section */}
          <div className="flex items-center space-x-6">
            <SaberLogo variant="primary" layout="horizontal" size="md" />
            <div className="hidden lg:flex items-center space-x-2">
              <div className="h-8 w-px bg-gray-300" />
              <div className="flex flex-col">
                <span className="text-xs font-semibold text-saber-blue uppercase tracking-wider">
                  Business Operations
                </span>
                <span className="text-sm text-gray-600">
                  EPC Partner Portal
                </span>
              </div>
            </div>
          </div>
          
          {/* User Section */}
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-700">Welcome, Partner</span>
            <button className="p-2 rounded-full hover:bg-gray-100">
              <Icon name="user" size={20} className="text-gray-600" />
            </button>
          </div>
        </div>
      </div>
    </div>
    
    {/* Navigation Bar */}
    <nav className="px-6 py-3 bg-gradient-to-r from-saber-blue/5 to-saber-green/5">
      <div className="flex space-x-6">
        <a href="#" className="text-sm font-medium text-saber-blue hover:text-saber-green transition-colors">
          Dashboard
        </a>
        <a href="#" className="text-sm font-medium text-gray-600 hover:text-saber-blue transition-colors">
          Projects
        </a>
        <a href="#" className="text-sm font-medium text-gray-600 hover:text-saber-blue transition-colors">
          Documents
        </a>
        <a href="#" className="text-sm font-medium text-gray-600 hover:text-saber-blue transition-colors">
          Training
        </a>
      </div>
    </nav>
  </header>
)

// Login Page with Logo
const EPCLoginPage = () => (
  <div className="min-h-screen bg-gradient-to-br from-saber-blue via-saber-gradient-dark to-saber-green">
    <div className="flex min-h-screen">
      {/* Left Panel - Branding */}
      <div className="hidden lg:flex lg:w-1/2 items-center justify-center p-12">
        <div className="max-w-md text-white">
          <SaberLogo variant="white" layout="stacked" size="lg" className="mb-8" />
          <h1 className="font-heading text-h2 mb-4">
            Welcome to the EPC Partner Portal
          </h1>
          <p className="font-body text-body-lg opacity-90">
            Your gateway to renewable energy project collaboration with Saber
          </p>
        </div>
      </div>
      
      {/* Right Panel - Login Form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-white">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <SaberLogo variant="primary" layout="horizontal" size="md" className="mx-auto mb-4" />
            <h2 className="font-heading text-h4 text-gray-900">Sign In</h2>
            <p className="text-sm text-gray-600 mt-2">
              Access your EPC partner account
            </p>
          </div>
          {/* Login form */}
        </div>
      </div>
    </div>
  </div>
)

// Mobile Responsive Logo
const ResponsiveLogo = () => (
  <>
    {/* Mobile: Compact or Symbol */}
    <div className="lg:hidden">
      <Sa# Saber Business Ops - Tailwind CSS Design System
## Complete Implementation Guide for Business Operations Platform

---

## Typography Setup

### Font Installation

```html
<!-- Add to your HTML head or import in CSS -->
<!-- Montserrat for Headings -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700;800&display=swap" rel="stylesheet">

<!-- Inter is included by default in Tailwind CSS, no import needed -->
<!-- Or if you want to explicitly load Inter with more weights: -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
```

### Why Inter for Body Text?
- **Superior screen legibility**: Designed specifically for digital interfaces
- **Excellent readability at small sizes**: Perfect for data-dense business applications
- **Modern, professional appearance**: Aligns with contemporary B2B platforms
- **Built into Tailwind**: No additional CDN load, better performance
- **Variable font support**: Smooth weight transitions

---

## 1. Brand Guidelines for Business Ops Platform

### Core Design Principles
- **Professional & Efficient**: Clean interfaces that prioritise functionality
- **Data-Dense Capable**: Support complex information without clutter
- **Accessibility First**: WCAG 2.1 AA compliant
- **Responsive**: Mobile-first approach, scaling to desktop
- **Performance**: Lightweight components, minimal animation

### Colour System

```javascript
// tailwind.config.js colour extensions
module.exports = {
  theme: {
    extend: {
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
      }
    }
  }
}
```

### Typography System

```javascript
// Typography configuration
module.exports = {
  theme: {
    extend: {
      fontFamily: {
        'heading': ['Montserrat', 'system-ui', 'sans-serif'],
        'body': ['Source Sans Pro', 'system-ui', 'sans-serif'],
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
      }
    }
  }
}
```

### Spacing & Layout System

```javascript
// Consistent spacing scale
module.exports = {
  theme: {
    extend: {
      spacing: {
        'xs': '0.25rem',   // 4px
        'sm': '0.5rem',    // 8px
        'md': '1rem',      // 16px
        'lg': '1.5rem',    // 24px
        'xl': '2rem',      // 32px
        '2xl': '3rem',     // 48px
        '3xl': '4rem',     // 64px
        'section': '5rem', // 80px
      }
    }
  }
}
```

---

## 2. Component Architecture

### Base Component Structure

```jsx
// components/ui/Button.jsx
const Button = ({ variant = 'primary', size = 'md', icon, children, ...props }) => {
  const variants = {
    primary: 'bg-saber-blue hover:bg-saber-blue/90 text-white',
    secondary: 'bg-saber-green hover:bg-saber-green/90 text-white',
    outline: 'border-2 border-saber-blue text-saber-blue hover:bg-saber-blue/10',
    ghost: 'text-saber-blue hover:bg-saber-blue/10',
    danger: 'bg-status-error hover:bg-status-error/90 text-white',
  }
  
  const sizes = {
    sm: 'px-3 py-1.5 text-body-sm',
    md: 'px-4 py-2 text-body',
    lg: 'px-6 py-3 text-body-lg',
  }
  
  return (
    <button
      className={`
        inline-flex items-center justify-center
        font-body font-medium
        rounded-md transition-all duration-200
        focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-saber-blue
        disabled:opacity-50 disabled:cursor-not-allowed
        ${variants[variant]}
        ${sizes[size]}
      `}
      {...props}
    >
      {icon && <span className="mr-2">{icon}</span>}
      {children}
    </button>
  )
}
```

### Icon Implementation Strategy

```jsx
// components/icons/IconProvider.jsx
import { createContext, useContext } from 'react'

// Create icon library context
const IconContext = createContext()

// Icon wrapper component
const Icon = ({ name, size = 20, className = '' }) => {
  const icons = useContext(IconContext)
  const IconComponent = icons[name]
  
  if (!IconComponent) {
    console.warn(`Icon "${name}" not found`)
    return null
  }
  
  return (
    <IconComponent 
      width={size} 
      height={size} 
      className={`inline-block ${className}`}
    />
  )
}

// Usage in components
<Icon name="solar" size={24} className="text-saber-green" />
```

---

## 3. Claude Code Implementation Instructions

### Project Structure

```bash
# Recommended project structure for Claude Code
/project-root
├── /src
│   ├── /components
│   │   ├── /ui           # Base UI components
│   │   ├── /layout       # Layout components
│   │   ├── /forms        # Form components
│   │   └── /business     # Business-specific components
│   ├── /templates        # Page templates
│   ├── /sections         # Reusable page sections
│   ├── /styles
│   │   └── globals.css   # Tailwind imports
│   └── /lib
│       └── /utils        # Helper functions
├── tailwind.config.js
└── .claude-instructions.md
```

### Claude Code Instructions File

Create a `.claude-instructions.md` file in your project root:

```markdown
# Saber Business Ops - Development Instructions

## Design System Rules
1. Always use Tailwind classes from our extended configuration
2. Never use emoji - only SVG icons from our icon library
3. Follow mobile-first responsive design
4. Use semantic HTML elements
5. Ensure WCAG 2.1 AA compliance

## Component Creation
When creating new components:
- Extend from base UI components where possible
- Use compound component patterns for complex UI
- Include proper TypeScript types
- Add JSDoc comments for props
- Follow naming convention: PascalCase for components

## Colour Usage
- Primary actions: saber-blue
- Secondary actions: saber-green
- Destructive actions: status-error
- Information: status-info
- Success states: status-success
- Warning states: status-warning

## Spacing Convention
- Component internal padding: p-md (1rem)
- Section spacing: space-y-lg (1.5rem)
- Card spacing: p-lg (1.5rem)
- Form field spacing: space-y-sm (0.5rem)

## Typography Rules
- Headings: font-heading with appropriate h1-h6 size
- Body text: font-body with body/body-sm/body-lg
- Monospace (data/codes): font-mono
- Always use text-primary for main content

## State Management
- Loading states: opacity-50 with spinner
- Disabled states: opacity-50 cursor-not-allowed
- Hover states: Use /90 opacity or /10 for backgrounds
- Focus states: ring-2 ring-saber-blue

## Responsive Breakpoints
- Mobile first: default styles
- sm: 640px+ (tablet portrait)
- md: 768px+ (tablet landscape)
- lg: 1024px+ (desktop)
- xl: 1280px+ (wide desktop)
```

### Template Creation Guide

```jsx
// templates/DashboardTemplate.jsx
const DashboardTemplate = ({ children, sidebar, header }) => {
  return (
    <div className="min-h-screen bg-ops-surface">
      {/* Header */}
      <header className="bg-white border-b border-ops-border">
        <div className="px-md py-sm lg:px-lg">
          {header}
        </div>
      </header>
      
      {/* Main Layout */}
      <div className="flex">
        {/* Sidebar */}
        <aside className="hidden md:block w-64 bg-white border-r border-ops-border min-h-[calc(100vh-4rem)]">
          <div className="p-md">
            {sidebar}
          </div>
        </aside>
        
        {/* Main Content */}
        <main className="flex-1 p-md lg:p-lg">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
```

### Section Components

```jsx
// sections/DataTable.jsx
const DataTable = ({ columns, data, actions }) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-ops-border overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-ops-surface border-b border-ops-border">
            <tr>
              {columns.map(col => (
                <th key={col.key} className="px-md py-sm text-left">
                  <span className="font-heading text-body-sm font-semibold text-text-secondary">
                    {col.label}
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-ops-border">
            {data.map((row, idx) => (
              <tr key={idx} className="hover:bg-ops-surface/50 transition-colors">
                {columns.map(col => (
                  <td key={col.key} className="px-md py-sm">
                    <span className="font-body text-body text-text-primary">
                      {row[col.key]}
                    </span>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
```

---

## 4. Conversion Best Practices

### Step-by-Step Migration

1. **Audit Current Styles**
   ```bash
   # Extract all existing CSS classes
   # Document current component patterns
   # Identify reusable patterns
   ```

2. **Setup Tailwind Configuration**
   ```bash
   npm install -D tailwindcss postcss autoprefixer
   npx tailwindcss init -p
   # Copy the extended configuration above
   ```

3. **Create Component Library**
   ```bash
   # Start with atomic components
   Button, Input, Card, Badge, Alert
   
   # Build composite components
   Form, Table, Modal, Dropdown
   
   # Create layout components
   Header, Sidebar, Footer, Container
   ```

4. **Progressive Migration**
   ```jsx
   // Wrap existing components during migration
   const LegacyWrapper = ({ children }) => (
     <div className="[&>*]:transition-all">
       {children}
     </div>
   )
   ```

### Utility Helpers

```javascript
// lib/utils/cn.js - Class name helper
export function cn(...classes) {
  return classes.filter(Boolean).join(' ')
}

// Usage
<div className={cn(
  'base-classes',
  condition && 'conditional-classes',
  className
)} />
```

### Performance Optimisation

```javascript
// tailwind.config.js - Purge configuration
module.exports = {
  content: [
    './src/**/*.{js,jsx,ts,tsx}',
    './public/index.html',
  ],
  // Enable JIT mode for optimal performance
  mode: 'jit',
}
```

---

## 5. Quick Reference Card

### Common Patterns

```jsx
// Status Badge
<span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-caption font-medium bg-status-success/10 text-status-success">
  Active
</span>

// Card Container
<div className="bg-white rounded-lg shadow-sm border border-ops-border p-lg">
  {/* Content */}
</div>

// Card with Gradient Header
<div className="bg-white rounded-lg shadow-sm overflow-hidden">
  <div className="h-2 bg-gradient-energy" />
  <div className="p-lg">
    {/* Content */}
  </div>
</div>

// Premium Card with Gradient Border
<div className="p-[1px] bg-gradient-brand rounded-lg">
  <div className="bg-white rounded-lg p-lg">
    <h3 className="font-heading text-h4 text-saber-blue">Premium Feature</h3>
    <p className="font-body text-body text-text-secondary mt-sm">Enhanced capabilities for your business</p>
  </div>
</div>

// CTA Section with Gradient
<section className="relative bg-gradient-brand rounded-lg p-xl my-lg overflow-hidden">
  <div className="absolute inset-0 bg-gradient-mesh opacity-20" />
  <div className="relative z-10 text-center">
    <h2 className="font-heading text-h2 text-white mb-md">Ready to Transform Your Energy?</h2>
    <button className="bg-white text-saber-blue hover:bg-saber-green hover:text-white px-lg py-md rounded-md font-semibold transition-all duration-300">
      Get Started Today
    </button>
  </div>
</section>

// Form Field
<div className="space-y-xs">
  <label className="block font-body text-body-sm font-medium text-text-secondary">
    Label
  </label>
  <input className="w-full px-md py-sm border border-ops-border rounded-md focus:ring-2 focus:ring-saber-blue focus:border-transparent" />
</div>

// Loading State
<div className="animate-pulse bg-ops-surface rounded-md h-10 w-full" />

// Empty State with Gradient Accent
<div className="text-center py-2xl relative">
  <div className="absolute inset-0 bg-gradient-mesh opacity-5" />
  <div className="relative">
    <div className="w-16 h-16 mx-auto mb-md bg-gradient-energy rounded-full opacity-20" />
    <Icon name="empty" size={48} className="mx-auto text-text-tertiary mb-md" />
    <h3 className="font-heading text-h5 text-text-primary mb-sm">No data found</h3>
    <p className="font-body text-body text-text-secondary mb-md">Try adjusting your filters</p>
    <p className="font-body text-caption text-text-tertiary italic">Infinite Power in Partnership</p>
  </div>
</div>

// Dashboard Welcome Card
<div className="bg-gradient-brand text-white rounded-lg p-lg mb-lg">
  <h2 className="font-heading text-h3 mb-sm">Welcome to Your Dashboard</h2>
  <p className="font-body text-body-lg mb-md">
    Track your renewable energy projects and collaborate with Saber
  </p>
  <p className="font-body text-body italic opacity-90">
    Infinite Power in Partnership
  </p>
</div>

// Partner Onboarding Screen
<div className="max-w-2xl mx-auto text-center py-xl">
  <SaberLogo variant="primary" size="lg" className="mb-lg" />
  <h1 className="font-heading text-h1 text-text-primary mb-md">
    Welcome to the Saber Partner Network
  </h1>
  <p className="font-body text-body-lg text-text-secondary mb-sm">
    Join us in transforming the UK's renewable energy landscape
  </p>
  <p className="font-heading text-h5 text-saber-green italic">
    Infinite Power in Partnership
  </p>
</div>

// Dashboard Metric Card with Gradient
<div className="relative bg-white rounded-lg p-lg shadow-sm overflow-hidden">
  <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-glow opacity-10 blur-2xl" />
  <div className="relative">
    <p className="font-body text-body-sm text-text-secondary mb-xs">Total Energy Saved</p>
    <p className="font-heading text-h2 text-saber-blue">847 MWh</p>
    <div className="flex items-center mt-sm">
      <span className="text-status-success text-body-sm font-semibold">+12.5%</span>
      <span className="text-text-tertiary text-caption ml-sm">vs last month</span>
    </div>
  </div>
</div>
```

### Responsive Utilities

```jsx
// Mobile-first responsive design
<div className="
  grid grid-cols-1 gap-md
  sm:grid-cols-2 sm:gap-lg
  lg:grid-cols-3
  xl:grid-cols-4
">
  {/* Grid items */}
</div>
```

---

## Implementation Checklist

- [ ] Install and configure Tailwind CSS
- [ ] Add custom colour palette to config
- [ ] Import and configure fonts (Montserrat, Source Sans Pro)
- [ ] **Set up logo system with all variants (full, horizontal, stacked, icon)**
- [ ] **Create logo component with theme and size variants**
- [ ] **Implement clear space and minimum size guidelines**
- [ ] Set up icon library system (NO EMOJIS)
- [ ] Create base component library
- [ ] Build page templates with proper logo placement
- [ ] **Configure favicon and PWA icons**
- [ ] Migrate existing components progressively
- [ ] Add accessibility testing
- [ ] Optimise bundle size with PurgeCSS
- [ ] Document component usage

## Logo Don'ts

- **Never stretch or distort the logo**
- **Never change logo colours outside approved themes**
- **Never place logo on busy backgrounds**
- **Never use logo smaller than minimum sizes**
- **Never recreate logo with fonts**
- **Never add effects (shadows, glows, outlines)**
- **Never rotate the logo**
- **Never use old logo versions**

## Support & Maintenance

- Review design system quarterly
- Update Tailwind to latest stable version
- Maintain component storybook
- Regular accessibility audits
- Performance monitoring
- **Logo files managed centrally in /public/assets/logos/**
- **Always use SVG format for logos (except favicons)**