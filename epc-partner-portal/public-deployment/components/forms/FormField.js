/**
 * Saber Form Field Components
 * Professional form inputs for business operations
 */

class SaberFormField {
  constructor({
    type = 'text',
    id,
    name,
    label,
    placeholder = ' ',
    required = false,
    disabled = false,
    error = null,
    helperText = null,
    className = '',
    ...props
  }) {
    this.type = type;
    this.id = id;
    this.name = name;
    this.label = label;
    this.placeholder = placeholder;
    this.required = required;
    this.disabled = disabled;
    this.error = error;
    this.helperText = helperText;
    this.className = className;
    this.props = props;
  }
  
  getInputClasses() {
    const baseClasses = 'w-full px-md py-sm border rounded-md focus:ring-2 focus:ring-offset-2 transition-all duration-200 font-body text-body placeholder-text-tertiary';
    const stateClasses = this.error 
      ? 'border-status-error focus:ring-status-error focus:border-status-error' 
      : 'border-ops-border focus:ring-saber-blue focus:border-transparent hover:border-saber-blue/50';
    const disabledClasses = this.disabled ? 'bg-ops-surface cursor-not-allowed opacity-60' : 'bg-white';
    
    return `${baseClasses} ${stateClasses} ${disabledClasses}`;
  }
  
  getLabelClasses() {
    const baseClasses = 'block font-body text-body-sm font-medium mb-xs';
    const stateClasses = this.error ? 'text-status-error' : 'text-text-secondary';
    return `${baseClasses} ${stateClasses}`;
  }
  
  renderInput() {
    const inputClasses = this.getInputClasses();
    const attributes = Object.entries(this.props)
      .map(([key, value]) => `${key}="${value}"`)
      .join(' ');
    
    const commonProps = `
      id="${this.id}"
      name="${this.name || this.id}"
      placeholder="${this.placeholder}"
      class="${inputClasses}"
      ${this.required ? 'required' : ''}
      ${this.disabled ? 'disabled' : ''}
      ${attributes}
    `;
    
    switch (this.type) {
      case 'textarea':
        return `<textarea ${commonProps} rows="${this.props.rows || 3}"></textarea>`;
      case 'select':
        const options = this.props.options || [];
        const optionsHtml = options.map(option => 
          `<option value="${option.value}" ${option.selected ? 'selected' : ''}>${option.label}</option>`
        ).join('');
        return `<select ${commonProps}>${optionsHtml}</select>`;
      default:
        return `<input type="${this.type}" ${commonProps} />`;
    }
  }
  
  renderFloatingLabel() {
    if (this.type === 'select' || this.type === 'textarea') {
      return this.renderStandardField();
    }
    
    return `
      <div class="form-field ${this.className}">
        <div class="relative">
          ${this.renderInput()}
          <label for="${this.id}" class="absolute left-md top-1/2 -translate-y-1/2 text-text-tertiary font-body text-body transition-all duration-200 pointer-events-none bg-white px-xs peer-focus:top-0 peer-focus:text-body-sm peer-focus:text-saber-blue peer-placeholder-shown:top-1/2 peer-[:not(:placeholder-shown)]:top-0 peer-[:not(:placeholder-shown)]:text-body-sm peer-[:not(:placeholder-shown)]:text-saber-blue">
            ${this.label}${this.required ? ' *' : ''}
          </label>
        </div>
        ${this.renderHelpers()}
      </div>
    `;
  }
  
  renderStandardField() {
    return `
      <div class="form-field ${this.className}">
        <label for="${this.id}" class="${this.getLabelClasses()}">
          ${this.label}${this.required ? ' *' : ''}
        </label>
        ${this.renderInput()}
        ${this.renderHelpers()}
      </div>
    `;
  }
  
  renderHelpers() {
    let helpersHtml = '';
    
    if (this.error) {
      helpersHtml += `<p class="mt-xs text-status-error text-body-sm font-medium flex items-center gap-1">
        <i class="fas fa-exclamation-circle"></i>
        ${this.error}
      </p>`;
    }
    
    if (this.helperText && !this.error) {
      helpersHtml += `<p class="mt-xs text-text-tertiary text-body-sm">
        ${this.helperText}
      </p>`;
    }
    
    return helpersHtml;
  }
  
  render(floatingLabel = false) {
    return floatingLabel ? this.renderFloatingLabel() : this.renderStandardField();
  }
  
  // Static factory methods for common field types
  static textField(id, label, options = {}) {
    return new SaberFormField({ type: 'text', id, label, ...options });
  }
  
  static emailField(id, label, options = {}) {
    return new SaberFormField({ type: 'email', id, label, ...options });
  }
  
  static phoneField(id, label, options = {}) {
    return new SaberFormField({ type: 'tel', id, label, ...options });
  }
  
  static numberField(id, label, options = {}) {
    return new SaberFormField({ type: 'number', id, label, ...options });
  }
  
  static dateField(id, label, options = {}) {
    return new SaberFormField({ type: 'date', id, label, ...options });
  }
  
  static passwordField(id, label, options = {}) {
    return new SaberFormField({ type: 'password', id, label, ...options });
  }
  
  static textareaField(id, label, options = {}) {
    return new SaberFormField({ type: 'textarea', id, label, ...options });
  }
  
  static selectField(id, label, options = [], fieldOptions = {}) {
    return new SaberFormField({ 
      type: 'select', 
      id, 
      label, 
      options: options.map(opt => ({
        value: opt.value || opt,
        label: opt.label || opt,
        selected: opt.selected || false
      })),
      ...fieldOptions 
    });
  }
}

/**
 * Checkbox Group Component
 */
class SaberCheckboxGroup {
  constructor({
    name,
    label,
    options = [],
    required = false,
    className = '',
    columns = 2
  }) {
    this.name = name;
    this.label = label;
    this.options = options;
    this.required = required;
    this.className = className;
    this.columns = columns;
  }
  
  render() {
    const gridClasses = `grid grid-cols-1 sm:grid-cols-${this.columns} gap-sm`;
    const optionsHtml = this.options.map((option, index) => `
      <label class="checkbox-item flex items-center gap-2 p-sm rounded-md hover:bg-ops-surface/50 transition-colors cursor-pointer">
        <input 
          type="checkbox" 
          name="${this.name}" 
          value="${option.value || option}"
          class="rounded border-ops-border text-saber-blue focus:ring-saber-blue focus:ring-offset-0"
          ${option.checked ? 'checked' : ''}
          ${this.required && index === 0 ? 'required' : ''}
        />
        <span class="font-body text-body text-text-primary select-none">
          ${option.label || option}
        </span>
      </label>
    `).join('');
    
    return `
      <div class="form-field ${this.className}">
        <label class="block font-body text-body-sm font-medium text-text-secondary mb-sm">
          ${this.label}${this.required ? ' *' : ''}
        </label>
        <div class="${gridClasses}">
          ${optionsHtml}
        </div>
      </div>
    `;
  }
}

/**
 * Radio Group Component
 */
class SaberRadioGroup {
  constructor({
    name,
    label,
    options = [],
    required = false,
    defaultValue = null,
    className = ''
  }) {
    this.name = name;
    this.label = label;
    this.options = options;
    this.required = required;
    this.defaultValue = defaultValue;
    this.className = className;
  }
  
  render() {
    const optionsHtml = this.options.map(option => `
      <label class="radio-item flex items-center gap-2 p-sm rounded-md hover:bg-ops-surface/50 transition-colors cursor-pointer">
        <input 
          type="radio" 
          name="${this.name}" 
          value="${option.value || option}"
          class="border-ops-border text-saber-blue focus:ring-saber-blue focus:ring-offset-0"
          ${this.required ? 'required' : ''}
          ${(option.value || option) === this.defaultValue ? 'checked' : ''}
        />
        <span class="font-body text-body text-text-primary select-none">
          ${option.label || option}
        </span>
      </label>
    `).join('');
    
    return `
      <div class="form-field ${this.className}">
        <label class="block font-body text-body-sm font-medium text-text-secondary mb-sm">
          ${this.label}${this.required ? ' *' : ''}
        </label>
        <div class="space-y-xs">
          ${optionsHtml}
        </div>
      </div>
    `;
  }
}

// Helper functions
function createFormField(containerId, field) {
  const container = document.getElementById(containerId);
  if (container) {
    container.innerHTML = field.render();
  }
}

function createCheckboxGroup(containerId, options) {
  const container = document.getElementById(containerId);
  if (container) {
    const group = new SaberCheckboxGroup(options);
    container.innerHTML = group.render();
  }
}

function createRadioGroup(containerId, options) {
  const container = document.getElementById(containerId);
  if (container) {
    const group = new SaberRadioGroup(options);
    container.innerHTML = group.render();
  }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { 
    SaberFormField, 
    SaberCheckboxGroup, 
    SaberRadioGroup, 
    createFormField, 
    createCheckboxGroup, 
    createRadioGroup 
  };
}

// Global access
if (typeof window !== 'undefined') {
  window.SaberFormField = SaberFormField;
  window.SaberCheckboxGroup = SaberCheckboxGroup;
  window.SaberRadioGroup = SaberRadioGroup;
  window.createFormField = createFormField;
  window.createCheckboxGroup = createCheckboxGroup;
  window.createRadioGroup = createRadioGroup;
}