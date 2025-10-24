<%@ Page Language="C#" %>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EPC Partner Onboarding | Saber Renewables</title>
    
    <style>
        /* Saber Brand Variables and Complete Styling */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Source Sans Pro', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #091922 0%, #0d1138 100%);
            min-height: 100vh;
        }

        /* Typography */
        h1, h2, h3 {
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        /* Container */
        .saber-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }

        /* Header */
        .saber-header {
            background: #044D73;
            box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .header-content {
            padding: 1.5rem 0;
            text-align: center;
        }

        .logo-section {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 2rem;
        }

        .saber-logo-svg {
            height: 50px;
            width: auto;
        }

        .tagline {
            font-weight: 600;
            color: white;
            font-size: 0.9rem;
            letter-spacing: 0.1em;
        }

        /* Hero Section */
        .hero-section {
            position: relative;
            padding: 4rem 0;
            overflow: hidden;
        }

        .energy-pulse {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(45deg, #7CC061, #044D73);
            opacity: 0.1;
            animation: pulse 4s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 0.05; transform: scale(1); }
            50% { opacity: 0.15; transform: scale(1.05); }
        }

        .hero-title {
            color: white;
            font-size: 2.5rem;
            margin-bottom: 1rem;
            text-align: center;
        }

        .hero-subtitle {
            color: rgba(255, 255, 255, 0.9);
            font-size: 1.2rem;
            text-align: center;
        }

        /* Form Section */
        .form-section {
            padding: 3rem 0 5rem;
        }

        .form-wrapper {
            max-width: 900px;
            margin: 0 auto;
        }

        /* Saber Card */
        .saber-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
            padding: 2.5rem;
            backdrop-filter: blur(10px);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
        }

        /* Progress Bar */
        .progress-bar {
            display: flex;
            justify-content: space-between;
            margin-bottom: 3rem;
            position: relative;
        }

        .progress-bar::before {
            content: '';
            position: absolute;
            top: 20px;
            left: 0;
            right: 0;
            height: 2px;
            background: #e0e0e0;
            z-index: 0;
        }

        .progress-step {
            display: flex;
            flex-direction: column;
            align-items: center;
            position: relative;
            z-index: 1;
            cursor: pointer;
        }

        .step-number {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: white;
            border: 2px solid #e0e0e0;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .progress-step.active .step-number {
            background: linear-gradient(135deg, #7CC061, #95D47E);
            color: white;
            border-color: #7CC061;
        }

        .progress-step.completed .step-number {
            background: #044D73;
            color: white;
            border-color: #044D73;
        }

        .step-label {
            margin-top: 0.5rem;
            font-size: 0.9rem;
            color: #666;
        }

        .progress-step.active .step-label {
            color: #7CC061;
            font-weight: 600;
        }

        /* Form Steps */
        .form-step {
            display: none;
            animation: fadeIn 0.5s ease;
        }

        .form-step.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Form Elements */
        .form-group {
            margin-bottom: 1.5rem;
        }

        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
        }

        label {
            display: block;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #333;
        }

        .required {
            color: #e74c3c;
        }

        input[type="text"],
        input[type="email"],
        input[type="tel"],
        input[type="number"],
        select,
        textarea {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1rem;
            transition: all 0.3s ease;
            background: white;
        }

        input:focus,
        select:focus,
        textarea:focus {
            outline: none;
            border-color: #7CC061;
            box-shadow: 0 0 0 3px rgba(124, 192, 97, 0.1);
        }

        textarea {
            resize: vertical;
            min-height: 120px;
        }

        /* Checkbox and Radio */
        .checkbox-group,
        .radio-group {
            display: flex;
            gap: 2rem;
            flex-wrap: wrap;
            margin-top: 0.5rem;
        }

        .checkbox-item,
        .radio-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        input[type="checkbox"],
        input[type="radio"] {
            width: 20px;
            height: 20px;
            cursor: pointer;
        }

        /* File Upload */
        .file-upload-area {
            border: 2px dashed #7CC061;
            border-radius: 12px;
            padding: 3rem;
            text-align: center;
            background: rgba(124, 192, 97, 0.05);
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .file-upload-area:hover {
            background: rgba(124, 192, 97, 0.1);
            border-color: #5ca047;
        }

        .file-upload-area.dragging {
            background: rgba(124, 192, 97, 0.2);
            border-color: #044D73;
        }

        .upload-icon {
            font-size: 3rem;
            color: #7CC061;
            margin-bottom: 1rem;
        }

        .uploaded-files {
            margin-top: 1.5rem;
        }

        .file-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.75rem;
            background: rgba(124, 192, 97, 0.1);
            border-radius: 8px;
            margin-bottom: 0.75rem;
        }

        /* Buttons */
        .button-group {
            display: flex;
            justify-content: space-between;
            margin-top: 2rem;
            padding-top: 2rem;
            border-top: 1px solid #e0e0e0;
        }

        .btn {
            padding: 0.75rem 2rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .btn-primary {
            background: linear-gradient(135deg, #7CC061, #5ca047);
            color: white;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(124, 192, 97, 0.3);
        }

        .btn-secondary {
            background: #f0f0f0;
            color: #333;
        }

        .btn-secondary:hover {
            background: #e0e0e0;
        }

        /* Success Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }

        .modal.show {
            display: flex;
            animation: fadeIn 0.3s ease;
        }

        .modal-content {
            background: white;
            border-radius: 16px;
            padding: 3rem;
            max-width: 500px;
            text-align: center;
            animation: slideUp 0.5s ease;
        }

        @keyframes slideUp {
            from { transform: translateY(50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }

        .success-icon {
            font-size: 4rem;
            color: #7CC061;
            margin-bottom: 1rem;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .form-row {
                grid-template-columns: 1fr;
            }
            
            .hero-title {
                font-size: 1.8rem;
            }
            
            .saber-card {
                padding: 1.5rem;
            }
        }
    </style>
</head>
<body>
    <!-- Header -->
    <header class="saber-header">
        <div class="saber-container">
            <div class="header-content">
                <div class="logo-section">
                    <svg class="saber-logo-svg" viewBox="0 0 495.2 101.48" xmlns="http://www.w3.org/2000/svg">
                        <g>
                            <path fill="#ffffff" d="M214.57,49.54c4.73,2.21,9.77,3.78,15.45,3.78s11.35-2.21,11.35-6.94-5.05-6.31-11.67-8.83c-8.2-3.15-17.34-7.25-17.34-18.92S221.82.03,232.86.03s13.56.95,20.18,3.47l-3.15,11.04c-5.05-1.89-9.77-3.15-15.77-3.15s-8.83,2.52-8.83,5.99c0,5.05,5.05,6.94,11.35,9.14,8.51,3.15,17.66,7.25,17.66,18.6s-10.09,19.86-23.65,19.86-15.14-2.21-19.86-5.05l4.1-10.09h0l-.32-.32Z"/>
                            <path fill="#ffffff" d="M284.26.98l13.24-.63,23.96,63.38-13.56.63-5.99-17.03h-21.76l-5.68,16.4h-13.56L284.26.98ZM298.44,36.61l-4.1-11.35-3.47-11.04-3.47,11.04-3.78,11.35h14.82Z"/>
                            <path fill="#ffffff" d="M331.24.98h21.44c13.87,0,21.13,5.68,21.13,15.77s-3.15,10.72-7.88,12.93h0c6.62,2.21,11.04,6.62,11.04,15.14s-9.14,19.23-23.02,19.23h-22.39V.98h-.32ZM355.2,26.52c4.1-1.26,5.68-4.1,5.68-7.88s-3.78-6.62-9.14-6.62h-7.88v14.19h11.35v.32ZM353.62,52.38c6.62,0,10.09-3.15,10.09-7.88s-3.78-6.62-8.83-7.25h-10.72v15.14h9.46Z"/>
                            <path fill="#ffffff" d="M389.89.98h39.1l-.63,11.35h-26.17v14.19h24.28v10.72h-24.28v15.14h28.06l-.63,11.35h-40.04V.98h.32Z"/>
                            <path fill="#ffffff" d="M443.49.98h20.81c15.77,0,23.96,6.62,23.96,18.92s-4.41,13.56-10.72,16.71l17.34,27.12-14.19.95-14.82-23.96h-9.77v23.02h-12.61V.98h0ZM468.08,29.67c4.1-1.26,6.94-4.1,6.94-8.83s-4.73-8.2-11.98-8.2h-6.94v17.34h11.98v-.32Z"/>
                            <circle fill="#7CC061" cx="50.75" cy="50.75" r="50.75"/>
                            <path fill="#ffffff" d="M28.06,24.28l40.84,8.3c1.72.35,1.7,2.81-.03,3.13l-17.41,3.18,28.43,23.84c1.42,1.19.37,3.46-1.43,3.08l-42.2-8.99c-1.75-.37-1.67-2.9.1-3.16l16.88-2.46L23.65,27.34c-1.37-1.21-.26-3.44,1.5-3.02l2.91-.04Z"/>
                        </g>
                    </svg>
                    <span class="tagline">Expert • Clear • Strategic</span>
                </div>
            </div>
        </div>
    </header>

    <!-- Hero Section -->
    <section class="hero-section">
        <div class="energy-pulse"></div>
        <div class="saber-container">
            <h1 class="hero-title">EPC Partner Onboarding</h1>
            <p class="hero-subtitle">Join Saber's network of certified Energy Performance Certificate partners</p>
        </div>
    </section>

    <!-- Main Form -->
    <main class="form-section">
        <div class="saber-container">
            <div class="form-wrapper saber-card">
                <!-- Progress Bar -->
                <div class="progress-bar">
                    <div class="progress-step active" data-step="1">
                        <span class="step-number">1</span>
                        <span class="step-label">Company Details</span>
                    </div>
                    <div class="progress-step" data-step="2">
                        <span class="step-number">2</span>
                        <span class="step-label">Capabilities</span>
                    </div>
                    <div class="progress-step" data-step="3">
                        <span class="step-number">3</span>
                        <span class="step-label">Documentation</span>
                    </div>
                    <div class="progress-step" data-step="4">
                        <span class="step-number">4</span>
                        <span class="step-label">Review & Submit</span>
                    </div>
                </div>

                <form id="epcOnboardingForm" action="#" method="post" onsubmit="return false;">
                    <!-- Step 1: Company Information -->
                    <div class="form-step active" data-step="1">
                        <h2>Company Information</h2>
                        <div class="form-row">
                            <div class="form-group">
                                <label for="companyName">Company Name <span class="required">*</span></label>
                                <input type="text" id="companyName" name="companyName" required>
                            </div>
                            <div class="form-group">
                                <label for="registrationNumber">Registration Number <span class="required">*</span></label>
                                <input type="text" id="registrationNumber" name="registrationNumber" required>
                            </div>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label for="contactName">Primary Contact Name <span class="required">*</span></label>
                                <input type="text" id="contactName" name="contactName" required>
                            </div>
                            <div class="form-group">
                                <label for="contactTitle">Contact Title <span class="required">*</span></label>
                                <input type="text" id="contactTitle" name="contactTitle" required>
                            </div>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label for="email">Email Address <span class="required">*</span></label>
                                <input type="email" id="email" name="email" required>
                            </div>
                            <div class="form-group">
                                <label for="phone">Phone Number <span class="required">*</span></label>
                                <input type="tel" id="phone" name="phone" required>
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label for="address">Business Address <span class="required">*</span></label>
                            <textarea id="address" name="address" required></textarea>
                        </div>
                    </div>

                    <!-- Step 2: Capabilities -->
                    <div class="form-step" data-step="2">
                        <h2>Service Capabilities</h2>
                        
                        <div class="form-group">
                            <label>EPC Services Offered <span class="required">*</span></label>
                            <div class="checkbox-group">
                                <div class="checkbox-item">
                                    <input type="checkbox" id="residential" name="services" value="residential">
                                    <label for="residential">Residential EPCs</label>
                                </div>
                                <div class="checkbox-item">
                                    <input type="checkbox" id="commercial" name="services" value="commercial">
                                    <label for="commercial">Commercial EPCs</label>
                                </div>
                                <div class="checkbox-item">
                                    <input type="checkbox" id="industrial" name="services" value="industrial">
                                    <label for="industrial">Industrial EPCs</label>
                                </div>
                            </div>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label for="yearsExperience">Years of Experience <span class="required">*</span></label>
                                <input type="number" id="yearsExperience" name="yearsExperience" min="0" required>
                            </div>
                            <div class="form-group">
                                <label for="teamSize">Team Size <span class="required">*</span></label>
                                <input type="number" id="teamSize" name="teamSize" min="1" required>
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label for="coverage">Geographic Coverage <span class="required">*</span></label>
                            <textarea id="coverage" name="coverage" placeholder="List regions/areas you service" required></textarea>
                        </div>
                        
                        <div class="form-group">
                            <label for="certifications">Certifications & Accreditations</label>
                            <textarea id="certifications" name="certifications" placeholder="List relevant certifications"></textarea>
                        </div>
                    </div>

                    <!-- Step 3: Documentation -->
                    <div class="form-step" data-step="3">
                        <h2>Required Documentation</h2>
                        
                        <div class="form-group">
                            <label>Upload Documents</label>
                            <div class="file-upload-area" id="dropZone">
                                <div class="upload-icon">📁</div>
                                <h3>Drop files here or click to browse</h3>
                                <p>Accepted formats: PDF, DOC, DOCX, JPG, PNG (Max 10MB per file)</p>
                                <input type="file" id="fileInput" multiple style="display: none;">
                            </div>
                            <div class="uploaded-files" id="uploadedFiles"></div>
                        </div>
                        
                        <div class="form-group">
                            <label for="additionalNotes">Additional Notes</label>
                            <textarea id="additionalNotes" name="additionalNotes" placeholder="Any additional information you'd like to provide"></textarea>
                        </div>
                    </div>

                    <!-- Step 4: Review & Submit -->
                    <div class="form-step" data-step="4">
                        <h2>Review & Submit</h2>
                        <div id="reviewContent">
                            <!-- Content will be populated by JavaScript -->
                        </div>
                        
                        <div class="form-group">
                            <div class="checkbox-item">
                                <input type="checkbox" id="terms" name="terms" required>
                                <label for="terms">I confirm that all information provided is accurate and complete</label>
                            </div>
                        </div>
                    </div>

                    <!-- Navigation Buttons -->
                    <div class="button-group">
                        <button type="button" class="btn btn-secondary" id="prevBtn" style="display: none;">Previous</button>
                        <button type="button" class="btn btn-primary" id="nextBtn">Next</button>
                        <button type="submit" class="btn btn-primary" id="submitBtn" style="display: none;">Submit Application</button>
                    </div>
                </form>
            </div>
        </div>
    </main>

    <!-- Success Modal -->
    <div class="modal" id="successModal">
        <div class="modal-content">
            <div class="success-icon">✓</div>
            <h2>Application Submitted Successfully!</h2>
            <p>Thank you for your interest in partnering with Saber Renewables. We'll review your application and contact you within 2-3 business days.</p>
            <button class="btn btn-primary" onclick="closeModal()">Close</button>
        </div>
    </div>

    <script>
        // SharePoint configuration
        const SHAREPOINT_BASE_URL = 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners';
        
        // Check authentication on page load
        window.addEventListener('DOMContentLoaded', function() {
            const isAuthenticated = sessionStorage.getItem('epcAuthenticated');
            if (!isAuthenticated) {
                window.location.href = SHAREPOINT_BASE_URL + '/SitePages/EPCVerifyAccess.aspx';
                return;
            }
        });

        let currentStep = 1;
        const totalSteps = 4;
        let uploadedFilesList = [];

        // Navigation
        document.getElementById('nextBtn').addEventListener('click', function() {
            if (validateStep(currentStep)) {
                if (currentStep < totalSteps) {
                    moveToStep(currentStep + 1);
                }
            }
        });

        document.getElementById('prevBtn').addEventListener('click', function() {
            if (currentStep > 1) {
                moveToStep(currentStep - 1);
            }
        });

        // Progress bar clicks
        document.querySelectorAll('.progress-step').forEach(step => {
            step.addEventListener('click', function() {
                const stepNum = parseInt(this.dataset.step);
                if (stepNum < currentStep || validateStep(currentStep)) {
                    moveToStep(stepNum);
                }
            });
        });

        function moveToStep(step) {
            // Update form steps
            document.querySelectorAll('.form-step').forEach(s => s.classList.remove('active'));
            document.querySelector(`.form-step[data-step="${step}"]`).classList.add('active');
            
            // Update progress bar
            document.querySelectorAll('.progress-step').forEach((s, index) => {
                s.classList.remove('active', 'completed');
                if (index + 1 < step) s.classList.add('completed');
                if (index + 1 === step) s.classList.add('active');
            });
            
            // Update buttons
            document.getElementById('prevBtn').style.display = step === 1 ? 'none' : 'block';
            document.getElementById('nextBtn').style.display = step === totalSteps ? 'none' : 'block';
            document.getElementById('submitBtn').style.display = step === totalSteps ? 'block' : 'none';
            
            // Update review if on last step
            if (step === 4) {
                updateReview();
            }
            
            currentStep = step;
        }

        function validateStep(step) {
            const currentStepEl = document.querySelector(`.form-step[data-step="${step}"]`);
            const requiredFields = currentStepEl.querySelectorAll('[required]');
            let valid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.style.borderColor = '#e74c3c';
                    valid = false;
                } else {
                    field.style.borderColor = '#e0e0e0';
                }
            });
            
            if (step === 2) {
                const checkboxes = currentStepEl.querySelectorAll('input[type="checkbox"]');
                const anyChecked = Array.from(checkboxes).some(cb => cb.checked);
                if (!anyChecked) {
                    alert('Please select at least one service capability');
                    valid = false;
                }
            }
            
            return valid;
        }

        function updateReview() {
            const formData = new FormData(document.getElementById('epcOnboardingForm'));
            let reviewHTML = '<div class="review-section">';
            
            reviewHTML += '<h3>Company Information</h3>';
            reviewHTML += `<p><strong>Company:</strong> ${formData.get('companyName')}</p>`;
            reviewHTML += `<p><strong>Contact:</strong> ${formData.get('contactName')} (${formData.get('contactTitle')})</p>`;
            reviewHTML += `<p><strong>Email:</strong> ${formData.get('email')}</p>`;
            reviewHTML += `<p><strong>Phone:</strong> ${formData.get('phone')}</p>`;
            
            reviewHTML += '<h3>Capabilities</h3>';
            const services = formData.getAll('services');
            reviewHTML += `<p><strong>Services:</strong> ${services.join(', ')}</p>`;
            reviewHTML += `<p><strong>Experience:</strong> ${formData.get('yearsExperience')} years</p>`;
            reviewHTML += `<p><strong>Team Size:</strong> ${formData.get('teamSize')}</p>`;
            
            if (uploadedFilesList.length > 0) {
                reviewHTML += '<h3>Uploaded Documents</h3>';
                reviewHTML += '<ul>';
                uploadedFilesList.forEach(file => {
                    reviewHTML += `<li>${file.name}</li>`;
                });
                reviewHTML += '</ul>';
            }
            
            reviewHTML += '</div>';
            document.getElementById('reviewContent').innerHTML = reviewHTML;
        }

        // File Upload
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');

        dropZone.addEventListener('click', () => fileInput.click());

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragging');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragging');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragging');
            handleFiles(e.dataTransfer.files);
        });

        fileInput.addEventListener('change', (e) => {
            handleFiles(e.target.files);
        });

        function handleFiles(files) {
            Array.from(files).forEach(file => {
                if (file.size <= 10485760) { // 10MB
                    uploadedFilesList.push(file);
                    displayFile(file);
                } else {
                    alert(`${file.name} exceeds 10MB limit`);
                }
            });
        }

        function displayFile(file) {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <span>${file.name} (${(file.size / 1024).toFixed(2)} KB)</span>
                <button type="button" onclick="removeFile('${file.name}', this)">Remove</button>
            `;
            document.getElementById('uploadedFiles').appendChild(fileItem);
        }

        function removeFile(fileName, button) {
            uploadedFilesList = uploadedFilesList.filter(f => f.name !== fileName);
            button.parentElement.remove();
        }

        // Form Submission
        document.getElementById('epcOnboardingForm').addEventListener('submit', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            if (!validateStep(4)) {
                alert('Please complete all required fields');
                return false;
            }
            
            if (!document.getElementById('terms').checked) {
                alert('Please confirm the information is accurate');
                return false;
            }
            
            // Show success modal
            document.getElementById('successModal').classList.add('show');
            
            // Clear session after submission
            setTimeout(() => {
                sessionStorage.clear();
                document.getElementById('epcOnboardingForm').reset();
                uploadedFilesList = [];
                document.getElementById('uploadedFiles').innerHTML = '';
            }, 3000);
            
            return false;
        });

        function closeModal() {
            document.getElementById('successModal').classList.remove('show');
            moveToStep(1);
        }
    </script>
</body>
</html>