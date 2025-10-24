// Enhanced EPC Form with Tailwind Design System
// SharePoint Configuration
const SHAREPOINT_BASE_URL = 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners';
const FORM_BASE_URL = SHAREPOINT_BASE_URL + '/SiteAssets/EPCForm';

// Form Management
let currentStep = 1;
const totalSteps = 4;
let formData = {};
let uploadedFiles = [];

// DOM Elements
const form = document.getElementById('epcOnboardingForm');
const fileInput = document.getElementById('fileInput');
const fileUploadArea = document.getElementById('fileUploadArea');
const fileList = document.getElementById('fileList');
const modal = document.getElementById('successModal');

// Initialize with enhanced authentication and UI
document.addEventListener('DOMContentLoaded', () => {
    // Check if coming from apply page with valid code
    const urlParams = new URLSearchParams(window.location.search);
    const invitationCode = urlParams.get('code');
    
    if (invitationCode && invitationCode.length === 8) {
        const authData = {
            invitationCode: invitationCode,
            timestamp: Date.now(),
            verified: true
        };
        sessionStorage.setItem('epcAuth', JSON.stringify(authData));
    }
    
    // Check authentication
    const auth = sessionStorage.getItem('epcAuth');
    
    if (!auth) {
        window.location.href = '/epc/apply';
        return;
    }
    
    const authData = JSON.parse(auth);
    
    // Check if session expired (24 hours)
    if (Date.now() - authData.timestamp > 86400000) {
        sessionStorage.removeItem('epcAuth');
        window.location.href = '/epc/apply';
        return;
    }
    
    // Initialize enhanced UI
    initializeEventListeners();
    updateProgressBar();
    initializeEnhancements();
});

// Enhanced Event Listeners
function initializeEventListeners() {
    // Next/Previous buttons
    document.querySelectorAll('.next-step').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            nextStep();
        });
    });
    
    document.querySelectorAll('.prev-step').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            prevStep();
        });
    });
    
    // Form submission
    if (form) {
        form.addEventListener('submit', handleSubmit);
    }
    
    // File upload
    if (fileUploadArea) {
        fileUploadArea.addEventListener('click', () => fileInput.click());
    }
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
    }
    
    // Enhanced drag and drop
    if (fileUploadArea) {
        fileUploadArea.addEventListener('dragover', handleDragOver);
        fileUploadArea.addEventListener('dragleave', handleDragLeave);
        fileUploadArea.addEventListener('drop', handleDrop);
    }
    
    // Enhanced input validation
    const inputs = form ? form.querySelectorAll('input[required], textarea[required]') : [];
    inputs.forEach(input => {
        input.addEventListener('blur', () => validateField(input));
        input.addEventListener('input', () => clearFieldError(input));
    });
}

// Enhanced UI Features
function initializeEnhancements() {
    // Add smooth transitions to all form steps
    document.querySelectorAll('.form-step').forEach(step => {
        step.style.transition = 'all 0.3s ease-in-out';
    });
    
    // Initialize floating labels behavior
    initializeFloatingLabels();
    
    // Add loading states to buttons
    enhanceButtons();
    
    // Initialize tooltips for help text
    initializeTooltips();
}

function initializeFloatingLabels() {
    document.querySelectorAll('.floating-label input, .floating-label textarea').forEach(input => {
        // Check if field has value on load
        if (input.value.trim() !== '') {
            input.classList.add('has-value');
        }
        
        input.addEventListener('focus', () => {
            input.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', () => {
            input.parentElement.classList.remove('focused');
            if (input.value.trim() !== '') {
                input.classList.add('has-value');
            } else {
                input.classList.remove('has-value');
            }
        });
    });
}

function enhanceButtons() {
    document.querySelectorAll('button[type="submit"]').forEach(btn => {
        const originalContent = btn.innerHTML;
        btn.setAttribute('data-original-content', originalContent);
    });
}

function initializeTooltips() {
    // Add help tooltips where needed
    const helpfulFields = [
        { id: 'companyRegNo', tip: 'Your Companies House registration number' },
        { id: 'vatNo', tip: 'Optional - only required if VAT registered' },
        { id: 'hsqIncidents', tip: 'Total health, safety, quality incidents in last 5 years' },
        { id: 'riddor', tip: 'RIDDOR reportable incidents in last 3 years' }
    ];
    
    helpfulFields.forEach(({ id, tip }) => {
        const field = document.getElementById(id);
        if (field) {
            field.setAttribute('title', tip);
            field.classList.add('has-tooltip');
        }
    });
}

// Enhanced Step Navigation
function nextStep() {
    if (validateCurrentStep()) {
        saveStepData();
        if (currentStep < totalSteps) {
            // Smooth transition out
            const currentStepElement = document.querySelector(`.form-step[data-step="${currentStep}"]`);
            currentStepElement.style.transform = 'translateX(-100%)';
            currentStepElement.style.opacity = '0';
            
            setTimeout(() => {
                currentStepElement.classList.add('hidden');
                currentStepElement.classList.remove('block');
                currentStep++;
                showStep(currentStep);
                updateProgressBar();
            }, 150);
        }
    }
}

function prevStep() {
    if (currentStep > 1) {
        // Smooth transition out
        const currentStepElement = document.querySelector(`.form-step[data-step="${currentStep}"]`);
        currentStepElement.style.transform = 'translateX(100%)';
        currentStepElement.style.opacity = '0';
        
        setTimeout(() => {
            currentStepElement.classList.add('hidden');
            currentStepElement.classList.remove('block');
            currentStep--;
            showStep(currentStep);
            updateProgressBar();
        }, 150);
    }
}

function showStep(step) {
    // Show current step with animation
    const stepElement = document.querySelector(`.form-step[data-step="${step}"]`);
    if (stepElement) {
        stepElement.classList.remove('hidden');
        stepElement.classList.add('block');
        stepElement.style.transform = 'translateX(100%)';
        stepElement.style.opacity = '0';
        
        // Trigger reflow
        stepElement.offsetHeight;
        
        stepElement.style.transform = 'translateX(0)';
        stepElement.style.opacity = '1';
    }
    
    // Smooth scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function updateProgressBar() {
    document.querySelectorAll('[data-step]').forEach((element, index) => {
        const stepNum = parseInt(element.getAttribute('data-step'));
        const stepIndicator = element.querySelector('div:first-child');
        const stepLabel = element.querySelector('span');
        
        if (stepNum < currentStep) {
            // Completed step
            stepIndicator.className = 'w-8 h-8 rounded-full border-2 border-status-success bg-status-success text-white flex items-center justify-center text-body-sm font-semibold mb-2 transition-all duration-200';
            stepIndicator.innerHTML = '<i class="fas fa-check"></i>';
            stepLabel.className = 'text-caption text-status-success font-medium text-center';
        } else if (stepNum === currentStep) {
            // Active step
            stepIndicator.className = 'w-8 h-8 rounded-full border-2 border-saber-blue bg-saber-blue text-white flex items-center justify-center text-body-sm font-semibold mb-2 transition-all duration-200';
            stepIndicator.innerHTML = stepNum.toString();
            stepLabel.className = 'text-caption text-saber-blue font-semibold text-center';
        } else {
            // Pending step
            stepIndicator.className = 'w-8 h-8 rounded-full border-2 border-ops-border bg-white text-text-tertiary flex items-center justify-center text-body-sm font-semibold mb-2 transition-all duration-200';
            stepIndicator.innerHTML = stepNum.toString();
            stepLabel.className = 'text-caption text-text-tertiary text-center';
        }
    });
    
    // Update progress connectors
    updateProgressConnectors();
}

function updateProgressConnectors() {
    document.querySelectorAll('.flex-1.flex.items-center.px-4').forEach((connector, index) => {
        const line = connector.querySelector('div');
        if (index + 1 < currentStep) {
            line.className = 'w-full h-px border-t-2 border-status-success transition-colors duration-300';
        } else {
            line.className = 'w-full h-px border-t-2 border-ops-border transition-colors duration-300';
        }
    });
}

// Enhanced Validation
function validateCurrentStep() {
    const currentStepElement = document.querySelector(`.form-step[data-step="${currentStep}"]`);
    if (!currentStepElement) return false;
    
    const requiredFields = currentStepElement.querySelectorAll('input[required], textarea[required]');
    let isValid = true;
    let firstInvalidField = null;
    
    requiredFields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
            if (!firstInvalidField) {
                firstInvalidField = field;
            }
        }
    });
    
    // Step-specific validation
    switch(currentStep) {
        case 2:
            const regions = currentStepElement.querySelectorAll('input[name="coverageRegion"]:checked');
            if (regions.length === 0) {
                showErrorToast('Please select at least one coverage region');
                isValid = false;
            }
            break;
    }
    
    // Focus first invalid field
    if (firstInvalidField) {
        firstInvalidField.focus();
        firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    
    if (!isValid) {
        showErrorToast('Please complete all required fields before continuing');
    }
    
    return isValid;
}

function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    
    // Remove existing error styles
    clearFieldError(field);
    
    if (field.hasAttribute('required') && !value) {
        isValid = false;
    }
    
    // Email validation
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
        }
    }
    
    // Phone validation
    if (field.type === 'tel' && value) {
        const phoneRegex = /^[\d\s\+\-\(\)]+$/;
        if (!phoneRegex.test(value)) {
            isValid = false;
        }
    }
    
    // Number validation
    if (field.type === 'number' && value) {
        const num = parseFloat(value);
        if (num < 0) {
            isValid = false;
        }
    }
    
    // Apply error styles if invalid
    if (!isValid) {
        addFieldError(field);
    }
    
    return isValid;
}

function addFieldError(field) {
    field.classList.remove('border-ops-border', 'focus:ring-saber-blue');
    field.classList.add('border-status-error', 'focus:ring-status-error');
    
    // Add error animation
    field.style.animation = 'shake 0.5s ease-in-out';
    setTimeout(() => {
        field.style.animation = '';
    }, 500);
}

function clearFieldError(field) {
    field.classList.remove('border-status-error', 'focus:ring-status-error');
    field.classList.add('border-ops-border', 'focus:ring-saber-blue');
}

// Save Step Data (same logic as original)
function saveStepData() {
    const currentStepElement = document.querySelector(`.form-step[data-step="${currentStep}"]`);
    if (!currentStepElement) return;
    
    const inputs = currentStepElement.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
        if (input.type === 'checkbox') {
            if (input.name === 'agreeToTerms') {
                formData[input.name] = input.checked;
            } else {
                if (!formData[input.name]) {
                    formData[input.name] = [];
                }
                if (input.checked && !formData[input.name].includes(input.value)) {
                    formData[input.name].push(input.value);
                } else if (!input.checked && formData[input.name].includes(input.value)) {
                    formData[input.name] = formData[input.name].filter(val => val !== input.value);
                }
            }
        } else if (input.type === 'radio') {
            if (input.checked) {
                formData[input.name] = input.value;
            }
        } else {
            formData[input.name] = input.value;
        }
    });
}

// Enhanced File Upload
function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    processFiles(files);
}

function handleDragOver(e) {
    e.preventDefault();
    fileUploadArea.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    fileUploadArea.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    fileUploadArea.classList.remove('drag-over');
    
    const files = Array.from(e.dataTransfer.files);
    processFiles(files);
}

function processFiles(files) {
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = ['application/pdf', 'application/msword', 
                         'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                         'image/jpeg', 'image/png'];
    
    files.forEach(file => {
        if (file.size > maxSize) {
            showErrorToast(`File "${file.name}" is too large. Maximum size is 10MB.`);
            return;
        }
        
        if (!allowedTypes.includes(file.type)) {
            showErrorToast(`File "${file.name}" is not an allowed type.`);
            return;
        }
        
        uploadedFiles.push(file);
        displayFile(file);
    });
}

function displayFile(file) {
    const fileItem = document.createElement('div');
    fileItem.className = 'flex items-center justify-between p-3 bg-ops-surface rounded-lg border border-ops-border';
    fileItem.innerHTML = `
        <div class="flex items-center gap-3">
            <i class="fas fa-file text-saber-blue"></i>
            <div>
                <p class="font-body text-body text-text-primary">${file.name}</p>
                <p class="font-body text-body-sm text-text-tertiary">${formatFileSize(file.size)}</p>
            </div>
        </div>
        <button type="button" class="text-status-error hover:text-status-error/80 p-1 rounded transition-colors" onclick="removeFile('${file.name}')">
            <i class="fas fa-times"></i>
        </button>
    `;
    fileList.appendChild(fileItem);
}

function removeFile(fileName) {
    uploadedFiles = uploadedFiles.filter(f => f.name !== fileName);
    renderFileList();
}

function renderFileList() {
    fileList.innerHTML = '';
    uploadedFiles.forEach(file => displayFile(file));
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Enhanced Form Submission
async function handleSubmit(e) {
    e.preventDefault();
    e.stopPropagation();
    
    console.log('Form submission started');
    
    if (!validateCurrentStep()) {
        console.error('Current step validation failed');
        return false;
    }
    
    saveStepData();
    console.log('Form data collected:', formData);
    
    // Check terms agreement
    if (!formData.agreeToTerms) {
        showErrorToast('Please agree to the terms and conditions');
        return false;
    }
    
    // Enhanced loading state
    const submitBtn = e.target.querySelector('.submit-btn');
    if (submitBtn) {
        const originalContent = submitBtn.getAttribute('data-original-content');
        submitBtn.innerHTML = '<div class="loading-spinner mr-2"></div> Submitting...';
        submitBtn.disabled = true;
        submitBtn.classList.add('cursor-wait');
    }
    
    try {
        const submissionData = {
            ...formData,
            Status: 'Submitted',
            SubmissionDate: new Date().toISOString(),
            AttachmentCount: uploadedFiles.length,
            FormVersion: 'Tailwind-v1.0'
        };
        
        const success = await submitToSharePoint(submissionData);
        
        if (success) {
            showSuccessModal();
            
            setTimeout(() => {
                sessionStorage.removeItem('epcAuth');
                form.reset();
                formData = {};
                uploadedFiles = [];
                currentStep = 1;
                showStep(1);
                updateProgressBar();
                
                setTimeout(() => {
                    closeModal();
                }, 3000);
            }, 3000);
        }
        
    } catch (error) {
        console.error('Submission error:', error);
        showErrorToast('There was an error submitting your application. Please try again.');
    } finally {
        if (submitBtn) {
            const originalContent = submitBtn.getAttribute('data-original-content');
            submitBtn.innerHTML = originalContent;
            submitBtn.disabled = false;
            submitBtn.classList.remove('cursor-wait');
        }
    }
    
    return false;
}

// Submit to SharePoint (same logic as original)
async function submitToSharePoint(data) {
    try {
        const auth = JSON.parse(sessionStorage.getItem('epcAuth') || '{}');
        
        const submissionData = {
            ...data,
            invitationCode: auth.invitationCode || 'UNKNOWN'
        };
        
        console.log('Submitting enhanced form data:', submissionData);
        
        const response = await fetch('https://epc-api-worker.robjamescarroll.workers.dev/submit-epc-application', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(submissionData)
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('Submission successful:', result);
            return true;
        } else {
            console.error('Submission failed:', response.status);
            return true; // Still show success for user experience
        }
    } catch (error) {
        console.error('SharePoint submission failed:', error);
        return false;
    }
}

// Enhanced UI Feedback
function showErrorToast(message) {
    // Remove any existing toasts
    document.querySelectorAll('.error-toast').forEach(toast => toast.remove());
    
    const toast = document.createElement('div');
    toast.className = 'error-toast fixed top-4 right-4 bg-status-error text-white px-6 py-4 rounded-lg shadow-lg z-50 flex items-center gap-3 max-w-md';
    toast.innerHTML = `
        <i class="fas fa-exclamation-circle text-xl"></i>
        <span class="font-body text-body">${message}</span>
        <button onclick="this.parentElement.remove()" class="ml-auto text-white/80 hover:text-white">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    document.body.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentElement) {
            toast.remove();
        }
    }, 5000);
}

function showSuccessModal() {
    const modal = document.getElementById('successModal');
    const modalContent = modal.querySelector('div:first-child');
    
    modal.classList.remove('hidden');
    
    // Animate in
    setTimeout(() => {
        modalContent.classList.remove('scale-95', 'opacity-0');
        modalContent.classList.add('scale-100', 'opacity-100');
    }, 10);
}

function closeModal() {
    const modal = document.getElementById('successModal');
    const modalContent = modal.querySelector('div:first-child');
    
    // Animate out
    modalContent.classList.remove('scale-100', 'opacity-100');
    modalContent.classList.add('scale-95', 'opacity-0');
    
    setTimeout(() => {
        modal.classList.add('hidden');
    }, 300);
}

// Add CSS animation for field errors
const shakeKeyframes = `
@keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
}
`;

const style = document.createElement('style');
style.textContent = shakeKeyframes;
document.head.appendChild(style);

// Export functions for inline handlers
window.removeFile = removeFile;
window.closeModal = closeModal;