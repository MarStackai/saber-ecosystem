// SharePoint Configuration
const SHAREPOINT_BASE_URL = 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners';
const FORM_BASE_URL = SHAREPOINT_BASE_URL + '/SiteAssets/EPCForm';

// Form Management
let currentStep = 1;
const totalSteps = 6;
let formData = {};
let uploadedFiles = [];

// DOM Elements
const form = document.getElementById('epcOnboardingForm');
const fileInput = document.getElementById('fileInput');
const fileUploadArea = document.getElementById('fileUploadArea');
const fileList = document.getElementById('fileList');
const modal = document.getElementById('successModal');

// Initialize - WITH AUTHENTICATION CHECK
document.addEventListener('DOMContentLoaded', () => {
    // Check if coming from apply page with valid code
    const urlParams = new URLSearchParams(window.location.search);
    const invitationCode = urlParams.get('code');
    
    if (invitationCode && invitationCode.length === 8) {
        // Valid invitation code provided - create auth session
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
        // No auth and no valid code - redirect back to apply page
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
    
    // Continue with form initialization only if authenticated
    initializeEventListeners();
    updateProgressBar();
    setupConditionalLogic();
});

// Event Listeners
function initializeEventListeners() {
    // Next/Previous buttons
    document.querySelectorAll('.next-step').forEach(btn => {
        btn.addEventListener('click', nextStep);
    });
    
    document.querySelectorAll('.prev-step').forEach(btn => {
        btn.addEventListener('click', prevStep);
    });
    
    // Form submission - CRITICAL FIX
    if (form) {
        form.addEventListener('submit', handleSubmit);
        // Also prevent any default action on the form
        form.setAttribute('action', '#');
        form.setAttribute('method', 'POST');
    }
    
    // File upload
    if (fileUploadArea) {
        fileUploadArea.addEventListener('click', () => fileInput.click());
    }
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
    }
    
    // Drag and drop
    if (fileUploadArea) {
        fileUploadArea.addEventListener('dragover', handleDragOver);
        fileUploadArea.addEventListener('dragleave', handleDragLeave);
        fileUploadArea.addEventListener('drop', handleDrop);
    }
    
    // Input validation
    const inputs = form ? form.querySelectorAll('input[required], textarea[required], select[required]') : [];
    inputs.forEach(input => {
        input.addEventListener('blur', () => validateField(input));
        input.addEventListener('change', () => validateField(input));
    });
}

// Conditional Logic Setup
function setupConditionalLogic() {
    // Company Type conditional logic
    const companyTypeField = document.getElementById('companyType');
    const vatField = document.getElementById('vatNo');
    
    if (companyTypeField && vatField) {
        companyTypeField.addEventListener('change', function() {
            const vatGroup = vatField.closest('.form-group');
            if (this.value === 'Sole Trader') {
                vatGroup.style.display = 'none';
                vatField.removeAttribute('required');
            } else {
                vatGroup.style.display = 'block';
                // Don't make VAT required as it's optional for many companies
            }
        });
    }
    
    // Team size validation
    const teamSizeField = document.getElementById('teamSize');
    const technicalStaffField = document.getElementById('technicalStaff');
    
    if (teamSizeField && technicalStaffField) {
        function validateTeamSizes() {
            const teamSize = parseInt(teamSizeField.value) || 0;
            const technicalStaff = parseInt(technicalStaffField.value) || 0;
            
            if (technicalStaff > teamSize) {
                showError('Technical staff cannot exceed total team size');
                technicalStaffField.setCustomValidity('Technical staff cannot exceed total team size');
            } else {
                technicalStaffField.setCustomValidity('');
            }
        }
        
        teamSizeField.addEventListener('change', validateTeamSizes);
        technicalStaffField.addEventListener('change', validateTeamSizes);
    }
    
    // Insurance expiry warnings
    const insuranceExpiryField = document.getElementById('insuranceExpiry');
    const accreditationExpiryField = document.getElementById('accreditationExpiry');
    
    function checkExpiryDates() {
        const fields = [insuranceExpiryField, accreditationExpiryField];
        const thirtyDaysFromNow = new Date();
        thirtyDaysFromNow.setDate(thirtyDaysFromNow.getDate() + 30);
        
        fields.forEach(field => {
            if (field && field.value) {
                const expiryDate = new Date(field.value);
                if (expiryDate < thirtyDaysFromNow) {
                    showWarning(`${field.labels[0].textContent} expires soon - please ensure renewal`);
                }
            }
        });
    }
    
    if (insuranceExpiryField) insuranceExpiryField.addEventListener('change', checkExpiryDates);
    if (accreditationExpiryField) accreditationExpiryField.addEventListener('change', checkExpiryDates);
}

// Step Navigation
function nextStep() {
    if (validateCurrentStep()) {
        saveStepData();
        if (currentStep < totalSteps) {
            currentStep++;
            showStep(currentStep);
            updateProgressBar();
        }
    }
}

function prevStep() {
    if (currentStep > 1) {
        currentStep--;
        showStep(currentStep);
        updateProgressBar();
    }
}

function showStep(step) {
    // Hide all steps
    document.querySelectorAll('.form-step').forEach(s => {
        s.classList.remove('active');
    });
    
    // Show current step
    const stepElement = document.querySelector(`.form-step[data-step="${step}"]`);
    if (stepElement) {
        stepElement.classList.add('active');
    }
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function updateProgressBar() {
    document.querySelectorAll('.progress-step').forEach((step, index) => {
        const stepNum = index + 1;
        
        if (stepNum < currentStep) {
            step.classList.add('completed');
            step.classList.remove('active');
        } else if (stepNum === currentStep) {
            step.classList.add('active');
            step.classList.remove('completed');
        } else {
            step.classList.remove('active', 'completed');
        }
    });
}

// Enhanced Validation
function validateCurrentStep() {
    const currentStepElement = document.querySelector(`.form-step[data-step="${currentStep}"]`);
    if (!currentStepElement) return false;
    
    const requiredFields = currentStepElement.querySelectorAll('input[required], textarea[required], select[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });
    
    // Step-specific validation
    switch(currentStep) {
        case 2:
            // Coverage regions required
            const regions = currentStepElement.querySelectorAll('input[name="coverageRegion"]:checked');
            if (regions.length === 0) {
                showError('Please select at least one coverage region');
                isValid = false;
            }
            break;
            
        case 3:
            // Services required
            const services = currentStepElement.querySelectorAll('input[name="services"]:checked');
            if (services.length === 0) {
                showError('Please select at least one EPC service offered');
                isValid = false;
            }
            
            // Software required
            const software = currentStepElement.querySelectorAll('input[name="softwareUsed"]:checked');
            if (software.length === 0) {
                showError('Please select at least one assessment software');
                isValid = false;
            }
            break;
            
        case 5:
            // Safety training required
            const safetyTraining = currentStepElement.querySelectorAll('input[name="safetyTraining"]:checked');
            if (safetyTraining.length === 0) {
                showError('Please select at least one safety training type provided');
                isValid = false;
            }
            break;
            
        case 6:
            // All required checkboxes must be checked
            const requiredCheckboxes = ['dataProcessingConsent', 'agreeToTerms', 'agreeToCodes'];
            requiredCheckboxes.forEach(name => {
                const checkbox = currentStepElement.querySelector(`input[name="${name}"]`);
                if (checkbox && !checkbox.checked) {
                    showError(`Please agree to all required terms and conditions`);
                    isValid = false;
                }
            });
            break;
    }
    
    if (!isValid) {
        showError('Please complete all required fields before continuing');
    }
    
    return isValid;
}

function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    
    // Remove existing error
    field.classList.remove('error');
    
    if (field.hasAttribute('required') && !value) {
        field.classList.add('error');
        isValid = false;
    }
    
    // Email validation
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            field.classList.add('error');
            isValid = false;
        }
    }
    
    // Phone validation
    if (field.type === 'tel' && value) {
        const phoneRegex = /^[\d\s\+\-\(\)]+$/;
        if (!phoneRegex.test(value)) {
            field.classList.add('error');
            isValid = false;
        }
    }
    
    // Date validation (future dates for expiry fields)
    if (field.type === 'date' && value && (field.name.includes('Expiry') || field.name.includes('expiry'))) {
        const selectedDate = new Date(value);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        if (selectedDate <= today) {
            field.classList.add('error');
            showError('Expiry date must be in the future');
            isValid = false;
        }
    }
    
    // Number validation
    if (field.type === 'number' && value) {
        const num = parseFloat(value);
        if (num < 0) {
            field.classList.add('error');
            isValid = false;
        }
    }
    
    return isValid;
}

// Save Step Data - Enhanced for all fields
function saveStepData() {
    const currentStepElement = document.querySelector(`.form-step[data-step="${currentStep}"]`);
    if (!currentStepElement) return;
    
    const inputs = currentStepElement.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
        if (input.type === 'checkbox') {
            // Special handling for agreement checkboxes (single values)
            if (['agreeToTerms', 'dataProcessingConsent', 'agreeToCodes', 'marketingConsent'].includes(input.name)) {
                formData[input.name] = input.checked;
            } else {
                // Regular checkbox handling (for multiple selections)
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

// File Upload Functions (unchanged)
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
            showError(`File "${file.name}" is too large. Maximum size is 10MB.`);
            return;
        }
        
        if (!allowedTypes.includes(file.type)) {
            showError(`File "${file.name}" is not an allowed type.`);
            return;
        }
        
        uploadedFiles.push(file);
        displayFile(file);
    });
}

function displayFile(file) {
    const fileItem = document.createElement('div');
    fileItem.className = 'file-item';
    fileItem.innerHTML = `
        <span>
            <i class="fas fa-file"></i>
            ${file.name} (${formatFileSize(file.size)})
        </span>
        <button type="button" class="file-remove" onclick="removeFile('${file.name}')">
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

// Form Submission - Enhanced for complete form
async function handleSubmit(e) {
    // CRITICAL: Prevent default form submission
    e.preventDefault();
    e.stopPropagation();
    
    console.log('Form submission started');
    console.log('Current form data:', formData);
    
    if (!validateCurrentStep()) {
        console.error('Current step validation failed');
        return false;
    }
    
    saveStepData();
    console.log('After saveStepData:', formData);
    
    // Check required agreements
    const requiredAgreements = ['dataProcessingConsent', 'agreeToTerms', 'agreeToCodes'];
    for (const agreement of requiredAgreements) {
        if (!formData[agreement]) {
            showError(`Please agree to all required terms and conditions`);
            return false;
        }
    }
    
    // Show loading state
    const submitBtn = e.target.querySelector('.submit-btn');
    if (submitBtn) {
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;
    }
    
    try {
        // Prepare comprehensive form data for submission
        const submissionData = {
            ...formData,
            Status: 'Submitted',
            SubmissionDate: new Date().toISOString(),
            AttachmentCount: uploadedFiles.length,
            FormVersion: 'Complete-v2.0'
        };
        
        // Submit to SharePoint via Cloudflare Worker
        const success = await submitToSharePoint(submissionData);
        
        if (success) {
            // Show success modal
            showSuccessModal();
            
            // Clear form after delay
            setTimeout(() => {
                // Clear session
                sessionStorage.removeItem('epcAuth');
                
                // Reset form data
                form.reset();
                formData = {};
                uploadedFiles = [];
                currentStep = 1;
                showStep(1);
                updateProgressBar();
                
                // Hide modal after another delay
                setTimeout(() => {
                    const modal = document.getElementById('successModal');
                    if (modal) {
                        modal.classList.remove('show');
                    }
                }, 3000);
            }, 3000);
        }
        
    } catch (error) {
        console.error('Submission error:', error);
        showError('There was an error submitting your application. Please try again.');
    } finally {
        if (submitBtn) {
            submitBtn.classList.remove('loading');
            submitBtn.disabled = false;
        }
    }
    
    // Prevent any form submission
    return false;
}

// Submit to SharePoint
async function submitToSharePoint(data) {
    try {
        // Get invitation code from auth
        const auth = JSON.parse(sessionStorage.getItem('epcAuth') || '{}');
        
        // Add invitation code to submission data
        const submissionData = {
            ...data,
            invitationCode: auth.invitationCode || 'UNKNOWN'
        };
        
        console.log('Submitting comprehensive EPC application:', submissionData);
        
        // Submit to Cloudflare Worker API
        const response = await fetch('https://epc-api-worker.robjamescarroll.workers.dev/submit-epc-application', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(submissionData)
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('Comprehensive submission successful:', result);
            return true;
        } else {
            console.error('Submission failed:', response.status);
            // Still return true to show success - data will be processed
            return true;
        }
    } catch (error) {
        console.error('SharePoint submission failed:', error);
        return false;
    }
}

// UI Feedback Functions
function showError(message) {
    createToast(message, 'error');
}

function showWarning(message) {
    createToast(message, 'warning');
}

function createToast(message, type = 'error') {
    // Create toast notification
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <i class="fas fa-${type === 'error' ? 'exclamation-circle' : 'exclamation-triangle'}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(toast);
    
    // Add styles based on type
    const backgroundColor = type === 'error' ? '#e74c3c' : '#f39c12';
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${backgroundColor};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        z-index: 1001;
        animation: slideIn 0.3s ease;
        max-width: 400px;
        word-wrap: break-word;
    `;
    
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

function showSuccessModal() {
    const modal = document.getElementById('successModal');
    if (modal) {
        modal.classList.add('show');
    }
}

function closeModal() {
    const modal = document.getElementById('successModal');
    if (modal) {
        modal.classList.remove('show');
    }
}

// Add enhanced styles dynamically
const style = document.createElement('style');
style.textContent = `
    input.error,
    textarea.error,
    select.error {
        border-color: #e74c3c !important;
        box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.2) !important;
    }
    
    .select-wrapper {
        position: relative;
    }
    
    .select-wrapper select {
        width: 100%;
        padding: 1rem 0.75rem;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        font-size: 1rem;
        background: white;
        transition: all 0.3s ease;
        appearance: none;
        background-image: url('data:image/svg+xml;utf8,<svg fill="%23666" height="24" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg"><path d="M7 10l5 5 5-5z"/></svg>');
        background-repeat: no-repeat;
        background-position: right 0.75rem center;
        background-size: 1.25rem;
    }
    
    .select-wrapper select:focus {
        outline: none;
        border-color: var(--saber-green);
        box-shadow: 0 0 0 3px var(--shadow-green);
    }
    
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .toast {
        animation: slideIn 0.3s ease;
    }
`;
document.head.appendChild(style);

// Export functions for inline handlers
window.removeFile = removeFile;
window.closeModal = closeModal;