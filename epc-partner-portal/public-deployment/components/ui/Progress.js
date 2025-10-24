/**
 * Saber Progress Components
 * Step indicators and progress tracking for business operations
 */

class SaberProgressBar {
  constructor({
    steps = [],
    currentStep = 1,
    completedSteps = [],
    variant = 'horizontal', // horizontal | vertical
    showLabels = true,
    className = ''
  }) {
    this.steps = steps;
    this.currentStep = currentStep;
    this.completedSteps = completedSteps;
    this.variant = variant;
    this.showLabels = showLabels;
    this.className = className;
  }
  
  getStepState(stepIndex) {
    const stepNumber = stepIndex + 1;
    
    if (this.completedSteps.includes(stepNumber) || stepNumber < this.currentStep) {
      return 'completed';
    } else if (stepNumber === this.currentStep) {
      return 'active';
    } else {
      return 'pending';
    }
  }
  
  getStepClasses(state) {
    const baseClasses = 'progress-step flex items-center transition-all duration-300';
    
    switch (state) {
      case 'completed':
        return `${baseClasses} progress-step-completed`;
      case 'active':
        return `${baseClasses} progress-step-active`;
      default:
        return `${baseClasses} progress-step-pending`;
    }
  }
  
  getNumberClasses(state) {
    const baseClasses = 'w-8 h-8 rounded-full border-2 flex items-center justify-center text-body-sm font-semibold transition-all duration-300';
    
    switch (state) {
      case 'completed':
        return `${baseClasses} border-status-success bg-status-success text-white shadow-sm`;
      case 'active':
        return `${baseClasses} border-saber-blue bg-saber-blue text-white shadow-brand`;
      default:
        return `${baseClasses} border-ops-border bg-white text-text-tertiary`;
    }
  }
  
  getLabelClasses(state) {
    const baseClasses = 'text-caption mt-sm text-center transition-all duration-300';
    
    switch (state) {
      case 'completed':
        return `${baseClasses} text-status-success font-medium`;
      case 'active':
        return `${baseClasses} text-saber-blue font-semibold`;
      default:
        return `${baseClasses} text-text-tertiary`;
    }
  }
  
  renderConnector(index, state, nextState) {
    if (index === this.steps.length - 1) return '';
    
    const isCompleted = state === 'completed';
    const connectorClasses = isCompleted 
      ? 'border-status-success' 
      : 'border-ops-border';
    
    if (this.variant === 'vertical') {
      return `
        <div class="flex justify-center py-sm">
          <div class="w-px h-8 border-l-2 ${connectorClasses} transition-colors duration-300"></div>
        </div>
      `;
    }
    
    return `
      <div class="flex-1 flex items-center px-sm">
        <div class="w-full h-px border-t-2 ${connectorClasses} transition-colors duration-300"></div>
      </div>
    `;
  }
  
  renderStep(step, index) {
    const state = this.getStepState(index);
    const stepNumber = index + 1;
    
    const iconContent = state === 'completed' 
      ? '<i class="fas fa-check"></i>'
      : stepNumber.toString();
    
    return `
      <div class="${this.getStepClasses(state)} ${this.variant === 'vertical' ? 'flex-col' : 'flex-col items-center flex-1'}">
        <div class="${this.getNumberClasses(state)}">
          ${iconContent}
        </div>
        ${this.showLabels ? `
          <div class="${this.getLabelClasses(state)}">
            ${step.label || step}
          </div>
        ` : ''}
      </div>
    `;
  }
  
  render() {
    const containerClasses = this.variant === 'vertical' 
      ? `space-y-sm ${this.className}`
      : `flex items-start justify-between ${this.className}`;
    
    let stepsHtml = '';
    
    this.steps.forEach((step, index) => {
      const state = this.getStepState(index);
      const nextState = index < this.steps.length - 1 ? this.getStepState(index + 1) : null;
      
      stepsHtml += this.renderStep(step, index);
      stepsHtml += this.renderConnector(index, state, nextState);
    });
    
    return `
      <div class="progress-bar-container ${containerClasses}" role="progressbar" aria-valuenow="${this.currentStep}" aria-valuemax="${this.steps.length}">
        ${stepsHtml}
      </div>
    `;
  }
  
  // Method to update the progress bar
  updateProgress(currentStep, completedSteps = []) {
    this.currentStep = currentStep;
    this.completedSteps = completedSteps;
    return this.render();
  }
  
  // Static factory methods
  static create(containerId, steps, options = {}) {
    const container = document.getElementById(containerId);
    if (container) {
      const progressBar = new SaberProgressBar({ steps, ...options });
      container.innerHTML = progressBar.render();
      return progressBar;
    }
    return null;
  }
}

/**
 * Simple Linear Progress Bar
 */
class SaberLinearProgress {
  constructor({
    value = 0,
    max = 100,
    showValue = true,
    variant = 'default', // default | success | warning | error
    size = 'md', // sm | md | lg
    className = ''
  }) {
    this.value = value;
    this.max = max;
    this.showValue = showValue;
    this.variant = variant;
    this.size = size;
    this.className = className;
  }
  
  getProgressClasses() {
    const variants = {
      default: 'bg-saber-blue',
      success: 'bg-status-success',
      warning: 'bg-status-warning',
      error: 'bg-status-error'
    };
    
    const sizes = {
      sm: 'h-1',
      md: 'h-2',
      lg: 'h-3'
    };
    
    return `${variants[this.variant]} ${sizes[this.size]} transition-all duration-300 rounded-full`;
  }
  
  getContainerClasses() {
    return `bg-ops-border rounded-full overflow-hidden ${this.className}`;
  }
  
  render() {
    const percentage = Math.min(100, Math.max(0, (this.value / this.max) * 100));
    
    return `
      <div class="linear-progress-container">
        ${this.showValue ? `
          <div class="flex justify-between items-center mb-xs">
            <span class="text-body-sm font-medium text-text-secondary">Progress</span>
            <span class="text-body-sm font-semibold text-text-primary">${Math.round(percentage)}%</span>
          </div>
        ` : ''}
        <div class="${this.getContainerClasses()}">
          <div 
            class="${this.getProgressClasses()}" 
            style="width: ${percentage}%"
            role="progressbar" 
            aria-valuenow="${this.value}" 
            aria-valuemax="${this.max}"
          ></div>
        </div>
      </div>
    `;
  }
  
  updateProgress(value) {
    this.value = value;
    return this.render();
  }
}

/**
 * Circular Progress Indicator
 */
class SaberCircularProgress {
  constructor({
    value = 0,
    max = 100,
    size = 'md', // sm | md | lg
    strokeWidth = 4,
    showValue = true,
    variant = 'default',
    className = ''
  }) {
    this.value = value;
    this.max = max;
    this.size = size;
    this.strokeWidth = strokeWidth;
    this.showValue = showValue;
    this.variant = variant;
    this.className = className;
  }
  
  getSizeConfig() {
    const configs = {
      sm: { radius: 20, viewBox: 50 },
      md: { radius: 30, viewBox: 70 },
      lg: { radius: 40, viewBox: 90 }
    };
    
    return configs[this.size];
  }
  
  getStrokeColor() {
    const colors = {
      default: '#044D73',
      success: '#10B981',
      warning: '#F59E0B',
      error: '#EF4444'
    };
    
    return colors[this.variant];
  }
  
  render() {
    const percentage = Math.min(100, Math.max(0, (this.value / this.max) * 100));
    const { radius, viewBox } = this.getSizeConfig();
    const circumference = 2 * Math.PI * radius;
    const strokeDasharray = circumference;
    const strokeDashoffset = circumference - (percentage / 100) * circumference;
    
    return `
      <div class="circular-progress flex items-center justify-center ${this.className}">
        <div class="relative">
          <svg width="${viewBox}" height="${viewBox}" class="transform -rotate-90">
            <!-- Background circle -->
            <circle
              cx="${viewBox / 2}"
              cy="${viewBox / 2}"
              r="${radius}"
              stroke="#E1E8ED"
              stroke-width="${this.strokeWidth}"
              fill="none"
            />
            <!-- Progress circle -->
            <circle
              cx="${viewBox / 2}"
              cy="${viewBox / 2}"
              r="${radius}"
              stroke="${this.getStrokeColor()}"
              stroke-width="${this.strokeWidth}"
              fill="none"
              stroke-linecap="round"
              stroke-dasharray="${strokeDasharray}"
              stroke-dashoffset="${strokeDashoffset}"
              class="transition-all duration-500 ease-out"
            />
          </svg>
          ${this.showValue ? `
            <div class="absolute inset-0 flex items-center justify-center">
              <span class="text-body-sm font-semibold text-text-primary">
                ${Math.round(percentage)}%
              </span>
            </div>
          ` : ''}
        </div>
      </div>
    `;
  }
}

// Helper functions
function createProgressBar(containerId, steps, options = {}) {
  return SaberProgressBar.create(containerId, steps, options);
}

function updateProgressBar(progressBarInstance, currentStep, completedSteps = []) {
  if (progressBarInstance) {
    const updatedHtml = progressBarInstance.updateProgress(currentStep, completedSteps);
    // Re-render if needed
    return updatedHtml;
  }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { 
    SaberProgressBar, 
    SaberLinearProgress, 
    SaberCircularProgress,
    createProgressBar,
    updateProgressBar
  };
}

// Global access
if (typeof window !== 'undefined') {
  window.SaberProgressBar = SaberProgressBar;
  window.SaberLinearProgress = SaberLinearProgress;
  window.SaberCircularProgress = SaberCircularProgress;
  window.createProgressBar = createProgressBar;
  window.updateProgressBar = updateProgressBar;
}