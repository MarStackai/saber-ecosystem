/**
 * Saber Button Component System
 * Professional button variants for business operations
 */

class SaberButton {
  constructor({
    variant = 'primary',  // primary | secondary | outline | ghost | danger
    size = 'md',         // sm | md | lg
    icon = null,         // Icon HTML or null
    disabled = false,
    loading = false,
    className = '',
    ...props
  }) {
    this.variant = variant;
    this.size = size;
    this.icon = icon;
    this.disabled = disabled;
    this.loading = loading;
    this.className = className;
    this.props = props;
  }
  
  getVariantClasses() {
    const variants = {
      primary: 'bg-saber-blue hover:bg-saber-blue/90 text-white shadow-brand hover:shadow-brand-lg',
      secondary: 'bg-saber-green hover:bg-saber-green/90 text-white shadow-energy hover:shadow-brand-lg',
      outline: 'border-2 border-saber-blue text-saber-blue hover:bg-saber-blue/10 hover:shadow-brand',
      ghost: 'text-saber-blue hover:bg-saber-blue/10',
      danger: 'bg-status-error hover:bg-status-error/90 text-white shadow-sm hover:shadow-md',
    };
    
    return variants[this.variant];
  }
  
  getSizeClasses() {
    const sizes = {
      sm: 'px-3 py-1.5 text-body-sm',
      md: 'px-4 py-2 text-body',
      lg: 'px-6 py-3 text-body-lg',
    };
    
    return sizes[this.size];
  }
  
  getBaseClasses() {
    return `
      inline-flex items-center justify-center gap-2
      font-body font-medium
      rounded-md transition-all duration-200
      focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-saber-blue
      disabled:opacity-50 disabled:cursor-not-allowed
      ${this.loading ? 'cursor-wait' : ''}
      ${this.disabled ? 'pointer-events-none' : 'interactive-subtle'}
    `.replace(/\s+/g, ' ').trim();
  }
  
  render(children, onClick = null) {
    const buttonClasses = [
      this.getBaseClasses(),
      this.getVariantClasses(),
      this.getSizeClasses(),
      this.className
    ].join(' ');
    
    const iconHtml = this.icon ? `<span class="icon">${this.icon}</span>` : '';
    const loadingSpinner = this.loading ? 
      '<span class="loading-spinner w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></span>' : '';
    
    const content = this.loading ? loadingSpinner : `${iconHtml}${children || ''}`;
    
    const attributes = Object.entries(this.props)
      .map(([key, value]) => `${key}="${value}"`)
      .join(' ');
    
    const onClickAttr = onClick ? `onclick="${onClick}"` : '';
    
    return `
      <button 
        class="${buttonClasses}"
        ${this.disabled ? 'disabled' : ''}
        ${attributes}
        ${onClickAttr}
      >
        ${content}
      </button>
    `;
  }
  
  // Static factory methods for common patterns
  static primary(text, options = {}) {
    return new SaberButton({ variant: 'primary', ...options }).render(text);
  }
  
  static secondary(text, options = {}) {
    return new SaberButton({ variant: 'secondary', ...options }).render(text);
  }
  
  static outline(text, options = {}) {
    return new SaberButton({ variant: 'outline', ...options }).render(text);
  }
  
  static ghost(text, options = {}) {
    return new SaberButton({ variant: 'ghost', ...options }).render(text);
  }
  
  static danger(text, options = {}) {
    return new SaberButton({ variant: 'danger', ...options }).render(text);
  }
  
  // Specialized buttons for common use cases
  static submit(text = 'Submit', options = {}) {
    return new SaberButton({ 
      variant: 'primary', 
      type: 'submit',
      icon: '<i class="fas fa-paper-plane"></i>',
      ...options 
    }).render(text);
  }
  
  static cancel(text = 'Cancel', options = {}) {
    return new SaberButton({ 
      variant: 'outline', 
      type: 'button',
      ...options 
    }).render(text);
  }
  
  static next(text = 'Next Step', options = {}) {
    return new SaberButton({ 
      variant: 'primary',
      icon: '<i class="fas fa-arrow-right"></i>',
      ...options 
    }).render(text);
  }
  
  static previous(text = 'Previous', options = {}) {
    return new SaberButton({ 
      variant: 'outline',
      icon: '<i class="fas fa-arrow-left"></i>',
      ...options 
    }).render(text);
  }
  
  static loading(text = 'Loading...', options = {}) {
    return new SaberButton({ 
      variant: 'primary',
      loading: true,
      disabled: true,
      ...options 
    }).render(text);
  }
}

// Helper function to create buttons and insert them into DOM
function createSaberButton(containerId, text, options = {}) {
  const container = document.getElementById(containerId);
  if (container) {
    const button = new SaberButton(options);
    container.innerHTML = button.render(text);
  }
}

// Enhanced button creation with event listeners
function createInteractiveButton(containerId, text, onClick, options = {}) {
  const container = document.getElementById(containerId);
  if (container) {
    const buttonId = `btn-${Math.random().toString(36).substr(2, 9)}`;
    const button = new SaberButton({ id: buttonId, ...options });
    container.innerHTML = button.render(text);
    
    // Add event listener
    const buttonElement = document.getElementById(buttonId);
    if (buttonElement && onClick) {
      buttonElement.addEventListener('click', onClick);
    }
  }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { SaberButton, createSaberButton, createInteractiveButton };
}

// Global access for direct HTML usage
if (typeof window !== 'undefined') {
  window.SaberButton = SaberButton;
  window.createSaberButton = createSaberButton;
  window.createInteractiveButton = createInteractiveButton;
}