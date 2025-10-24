/**
 * Premium EPC Form with TailwindPlus Elements
 * Enhanced user experience with accessibility and modern interactions
 */

// Form state management
let currentStep = 1;
const totalSteps = 4;
let formData = {};
let validationErrors = {};

// DOM Elements
const form = document.getElementById('epcOnboardingForm');
const progressBar = document.getElementById('progress-bar');
const currentStepText = document.getElementById('current-step');
const loadingOverlay = document.getElementById('loading-overlay');
const successModal = document.getElementById('success-modal');

// Enhanced form validation rules
const validationRules = {
    required: {
        test: (value) => value && value.trim().length > 0,
        message: 'This field is required'
    },
    email: {
        test: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
        message: 'Please enter a valid email address'
    },
    phone: {
        test: (value) => /^[\+]?[\d\s\-\(\)]{10,}$/.test(value),
        message: 'Please enter a valid phone number'
    },
    url: {
        test: (value) => /^https?:\/\/[^\s$.?#].[^\s]*$/i.test(value),
        message: 'Please enter a valid URL'
    }
};

// Initialize form when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeForm);

function initializeForm() {
    console.log('🚀 Premium EPC Form Initialized with TailwindPlus Elements');
    
    // Check authentication (simplified for demo)
    checkAuthentication();
    
    // Initialize form validation
    setupFormValidation();
    
    // Initialize step navigation
    setupStepNavigation();
    
    // Initialize enhanced interactions
    setupEnhancedInteractions();
    
    // Initialize accessibility features
    setupAccessibilityFeatures();
    
    // Initialize TailwindPlus dialog for success modal
    setupSuccessModal();
    
    console.log('✅ Form initialization complete');
}

function checkAuthentication() {
    // Simplified auth check for demo - in production this would be more robust
    const urlParams = new URLSearchParams(window.location.search);
    const invitationCode = urlParams.get('code');
    
    if (invitationCode && invitationCode.length === 8) {
        sessionStorage.setItem('epcAuth', JSON.stringify({
            invitationCode,
            timestamp: Date.now(),
            verified: true
        }));
        console.log('✅ Authentication verified with code:', invitationCode);
    } else {
        console.log('ℹ️ Demo mode - authentication bypassed');
    }
}

function setupFormValidation() {
    // Real-time validation for all form inputs
    const inputs = form.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
        // Add validation on blur for better UX
        input.addEventListener('blur', (e) => validateField(e.target));
        
        // Add validation on input for immediate feedback
        input.addEventListener('input', (e) => {
            if (validationErrors[e.target.name]) {
                validateField(e.target);
            }
        });
        
        // Enhanced focus states
        input.addEventListener('focus', (e) => {
            e.target.parentElement?.classList.add('field-focused');
        });
        
        input.addEventListener('blur', (e) => {
            e.target.parentElement?.classList.remove('field-focused');
        });
    });
}

function validateField(field) {
    const rules = field.dataset.validation?.split(',') || [];
    const value = field.value.trim();
    const fieldName = field.name;
    
    // Clear previous errors
    clearFieldError(field);
    delete validationErrors[fieldName];
    
    // Validate each rule
    for (const rule of rules) {
        const validator = validationRules[rule];
        if (validator && !validator.test(value)) {
            showFieldError(field, validator.message);
            validationErrors[fieldName] = validator.message;
            return false;
        }
    }
    
    // Show success state
    showFieldSuccess(field);
    return true;
}

function showFieldError(field, message) {
    field.classList.add('error');
    field.classList.remove('border-slate-300', 'focus:border-blue-500');
    field.classList.add('border-red-300', 'focus:border-red-500', 'focus:ring-red-500/20');
    
    const errorElement = field.parentElement.querySelector('.form-error');
    if (errorElement) {
        errorElement.querySelector('span').textContent = message;
        errorElement.classList.remove('hidden');
    }
}

function showFieldSuccess(field) {
    field.classList.remove('error');
    field.classList.remove('border-red-300', 'focus:border-red-500', 'focus:ring-red-500/20');
    field.classList.add('border-green-300', 'focus:border-green-500');
    
    const errorElement = field.parentElement.querySelector('.form-error');
    if (errorElement) {
        errorElement.classList.add('hidden');
    }
}

function clearFieldError(field) {
    field.classList.remove('error', 'border-red-300', 'focus:border-red-500', 'focus:ring-red-500/20');
    field.classList.remove('border-green-300', 'focus:border-green-500');
    
    const errorElement = field.parentElement.querySelector('.form-error');
    if (errorElement) {
        errorElement.classList.add('hidden');
    }
}

function setupStepNavigation() {
    // Next step button
    const nextButton = document.getElementById('nextStep1');
    if (nextButton) {
        nextButton.addEventListener('click', handleNextStep);
    }
    
    // Step indicators (for future steps)
    const stepIndicators = document.querySelectorAll('[data-step]');
    stepIndicators.forEach(indicator => {
        indicator.addEventListener('click', (e) => {
            const targetStep = parseInt(e.currentTarget.dataset.step);
            if (targetStep <= currentStep) {
                goToStep(targetStep);
            }
        });
    });
}

function handleNextStep() {
    // Validate current step
    if (validateCurrentStep()) {
        saveCurrentStepData();
        // For now, just show success since we only have step 1
        showSuccess();
    }
}

function validateCurrentStep() {
    const currentStepElement = document.getElementById(`step-${currentStep}`);
    const requiredFields = currentStepElement.querySelectorAll('[required], [data-validation*="required"]');
    
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });
    
    return isValid;
}

function saveCurrentStepData() {
    const currentStepElement = document.getElementById(`step-${currentStep}`);
    const inputs = currentStepElement.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
        formData[input.name] = input.value;
    });
    
    console.log('💾 Step data saved:', formData);
}

function goToStep(step) {
    currentStep = step;
    updateProgressIndicator();
    updateStepVisibility();
}

function updateProgressIndicator() {
    // Update progress bar
    const progressPercentage = (currentStep / totalSteps) * 100;
    if (progressBar) {
        progressBar.style.width = `${progressPercentage}%`;
    }
    
    // Update step text
    if (currentStepText) {
        currentStepText.textContent = currentStep;
    }
    
    // Update step indicators
    const stepIndicators = document.querySelectorAll('[data-step]');
    stepIndicators.forEach((indicator, index) => {
        const stepNum = index + 1;
        const indicatorElement = indicator.querySelector('.step-indicator');
        
        if (stepNum < currentStep) {
            indicatorElement.classList.add('completed');
            indicatorElement.classList.remove('active', 'pending');
        } else if (stepNum === currentStep) {
            indicatorElement.classList.add('active');
            indicatorElement.classList.remove('completed', 'pending');
        } else {
            indicatorElement.classList.add('pending');
            indicatorElement.classList.remove('active', 'completed');
        }
    });
}

function setupEnhancedInteractions() {
    // Smooth animations for form interactions
    const formGroups = document.querySelectorAll('.form-group');
    
    // Intersection Observer for fade-in animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in');
            }
        });
    }, observerOptions);
    
    formGroups.forEach(group => observer.observe(group));
    
    // Enhanced button interactions
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        button.addEventListener('mousedown', () => {
            button.style.transform = 'scale(0.98)';
        });
        
        button.addEventListener('mouseup', () => {
            button.style.transform = '';
        });
        
        button.addEventListener('mouseleave', () => {
            button.style.transform = '';
        });
    });
}

function setupAccessibilityFeatures() {
    // Keyboard navigation support
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && e.target.matches('input:not([type="textarea"])')) {
            e.preventDefault();
            const nextInput = getNextInput(e.target);
            if (nextInput) {
                nextInput.focus();
            } else {
                // If last input, trigger next step
                handleNextStep();
            }
        }
    });
    
    // Screen reader announcements
    const announceElement = createAnnouncementElement();
    
    function announce(message) {
        announceElement.textContent = message;
    }
    
    // Announce validation errors
    form.addEventListener('invalid', (e) => {
        const field = e.target;
        const label = field.parentElement.querySelector('label')?.textContent || field.name;
        announce(`Error in ${label}: ${validationErrors[field.name] || 'Please check this field'}`);
    }, true);
}

function createAnnouncementElement() {
    const element = document.createElement('div');
    element.setAttribute('aria-live', 'polite');
    element.setAttribute('aria-atomic', 'true');
    element.className = 'sr-only';
    document.body.appendChild(element);
    return element;
}

function getNextInput(currentInput) {
    const inputs = Array.from(form.querySelectorAll('input, textarea, select'));
    const currentIndex = inputs.indexOf(currentInput);
    return inputs[currentIndex + 1] || null;
}

function setupSuccessModal() {
    const closeModalButton = document.getElementById('close-modal');
    if (closeModalButton) {
        closeModalButton.addEventListener('click', closeSuccessModal);
    }
}

function showSuccess() {
    // Show loading overlay
    showLoadingOverlay('Submitting your application...');
    
    // Simulate API call
    setTimeout(async () => {
        try {
            // In real implementation, this would submit to the actual API
            const success = await submitToAPI();
            
            hideLoadingOverlay();
            
            if (success) {
                showSuccessModal();
            } else {
                showErrorMessage('There was an error submitting your application. Please try again.');
            }
        } catch (error) {
            hideLoadingOverlay();
            showErrorMessage('There was an error submitting your application. Please try again.');
        }
    }, 2000);
}

async function submitToAPI() {
    // For demo purposes, always return success
    // In production, this would submit to your actual API endpoint
    console.log('📤 Submitting form data:', formData);
    
    const submissionData = {
        ...formData,
        timestamp: new Date().toISOString(),
        source: 'premium-epc-portal',
        version: '2.0'
    };
    
    // Simulate API call to your actual endpoint
    // const response = await fetch('https://epc-api-worker.robjamescarroll.workers.dev/submit-epc-application', {
    //     method: 'POST',
    //     headers: {
    //         'Content-Type': 'application/json',
    //     },
    //     body: JSON.stringify(submissionData)
    // });
    
    // For demo, always succeed
    return true;
}

function showLoadingOverlay(message = 'Loading...') {
    if (loadingOverlay) {
        const messageElement = loadingOverlay.querySelector('p');
        if (messageElement) {
            messageElement.textContent = message;
        }
        loadingOverlay.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
}

function hideLoadingOverlay() {
    if (loadingOverlay) {
        loadingOverlay.classList.add('hidden');
        document.body.style.overflow = '';
    }
}

function showSuccessModal() {
    if (successModal && successModal.showModal) {
        successModal.showModal();
        
        // Focus management for accessibility
        const closeButton = successModal.querySelector('#close-modal');
        if (closeButton) {
            setTimeout(() => closeButton.focus(), 100);
        }
    }
}

function closeSuccessModal() {
    if (successModal && successModal.close) {
        successModal.close();
        
        // In a real application, this might redirect to a dashboard
        // window.location.href = '/dashboard';
    }
}

function showErrorMessage(message) {
    // Create a toast notification for errors
    const toast = createToast(message, 'error');
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

function createToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 z-50 max-w-sm bg-white border border-slate-200 rounded-xl shadow-lg p-4 transform translate-x-full transition-transform duration-300`;
    
    const icon = type === 'error' ? 'fas fa-exclamation-circle text-red-500' : 'fas fa-info-circle text-blue-500';
    
    toast.innerHTML = `
        <div class="flex items-center gap-3">
            <i class="${icon}"></i>
            <p class="text-slate-900 font-medium">${message}</p>
            <button class="ml-auto text-slate-400 hover:text-slate-600" onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    // Animate in
    setTimeout(() => {
        toast.classList.remove('translate-x-full');
    }, 10);
    
    return toast;
}

// Export functions for potential external use
window.EpcForm = {
    validateField,
    goToStep,
    showSuccess,
    closeSuccessModal
};

console.log('🎉 Premium EPC Form JavaScript loaded successfully');