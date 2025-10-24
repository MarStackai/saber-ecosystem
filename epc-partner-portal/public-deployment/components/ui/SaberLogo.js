/**
 * Saber Logo Component System
 * Provides consistent logo usage across all business operations interfaces
 */

class SaberLogo {
  constructor({ 
    variant = 'primary',     // primary | white | mono-blue | mono-green | symbol-only
    layout = 'horizontal',   // horizontal | stacked | compact
    size = 'md',            // xs | sm | md | lg | xl
    className = '' 
  }) {
    this.variant = variant;
    this.layout = layout;
    this.size = size;
    this.className = className;
  }
  
  // Logo paths based on actual Saber branding
  getLogoSrc() {
    const logoSrc = {
      primary: {
        horizontal: '../images/Saber-logo-wob-green.svg',
        stacked: '../images/Saber-logo-wob-green.svg',
        compact: '../images/Saber-logo-wob-green.svg',
      },
      white: {
        horizontal: '../images/Saber-logo-wob-green.svg',
        stacked: '../images/Saber-logo-wob-green.svg', 
        compact: '../images/Saber-logo-wob-green.svg',
      },
      'mono-blue': {
        horizontal: '../images/Saber-logo-wob-green.svg',
        stacked: '../images/Saber-logo-wob-green.svg',
        compact: '../images/Saber-logo-wob-green.svg',
      },
      'mono-green': {
        horizontal: '../images/Saber-logo-wob-green.svg',
        stacked: '../images/Saber-logo-wob-green.svg',
        compact: '../images/Saber-logo-wob-green.svg',
      },
      'symbol-only': {
        horizontal: '../images/Saber-logo-wob-green.svg',
        stacked: '../images/Saber-logo-wob-green.svg',
        compact: '../images/Saber-logo-wob-green.svg',
      }
    };
    
    return logoSrc[this.variant][this.layout];
  }
  
  getSizeClasses() {
    const sizes = {
      xs: 'w-logo-xs h-logo-xs',
      sm: 'w-logo-sm h-logo-sm',
      md: 'w-logo-md h-logo-md',
      lg: 'w-logo-lg h-logo-lg',
      xl: 'w-logo-xl h-logo-xl',
    };
    
    return sizes[this.size];
  }
  
  getAspectRatio() {
    const aspectRatios = {
      horizontal: 'aspect-[3.53/1]',  // Standard horizontal ratio
      stacked: 'aspect-[1.8/1]',      // Stacked version ratio
      compact: 'aspect-[2.5/1]',      // Compact version ratio
      'symbol-only': 'aspect-square', // Symbol is square
    };
    
    return aspectRatios[this.layout];
  }
  
  render() {
    return `
      <div class="inline-flex items-center ${this.className}">
        <img 
          src="${this.getLogoSrc()}"
          alt="Saber Renewable Energy"
          class="${this.getSizeClasses()} ${this.getAspectRatio()} object-contain"
        />
      </div>
    `;
  }
  
  // Static factory methods for common use cases
  static forHeader() {
    return new SaberLogo({
      variant: 'primary',
      layout: 'horizontal',
      size: 'md',
      className: 'transition-opacity hover:opacity-80'
    });
  }
  
  static forFooter() {
    return new SaberLogo({
      variant: 'primary',
      layout: 'compact',
      size: 'sm',
      className: 'opacity-75'
    });
  }
  
  static forHero() {
    return new SaberLogo({
      variant: 'primary',
      layout: 'horizontal',
      size: 'xl',
      className: 'animate-fade-in'
    });
  }
  
  static forMobile() {
    return new SaberLogo({
      variant: 'primary',
      layout: 'compact',
      size: 'sm'
    });
  }
}

// Helper function to easily insert logos in HTML
function insertSaberLogo(containerId, options = {}) {
  const container = document.getElementById(containerId);
  if (container) {
    const logo = new SaberLogo(options);
    container.innerHTML = logo.render();
  }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { SaberLogo, insertSaberLogo };
}

// Global access for direct HTML usage
if (typeof window !== 'undefined') {
  window.SaberLogo = SaberLogo;
  window.insertSaberLogo = insertSaberLogo;
}