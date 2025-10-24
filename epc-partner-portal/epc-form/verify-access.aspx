<%@ Page Language="C#" %>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EPC Partner Portal - Verify Access</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            width: 100%;
            max-width: 500px;
            padding: 40px;
            animation: slideIn 0.5s ease-out;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .saber-header {
            background: #044D73;
            margin: -40px -40px 30px -40px;
            padding: 30px 40px;
            border-radius: 20px 20px 0 0;
            text-align: center;
        }

        .logo-container {
            margin-bottom: 20px;
        }

        .saber-logo-svg {
            width: 200px;
            height: auto;
        }

        h1 {
            color: white;
            font-size: 24px;
            font-weight: 600;
            margin-top: 10px;
        }

        .form-group {
            margin-bottom: 25px;
        }

        label {
            display: block;
            color: #333;
            font-weight: 500;
            margin-bottom: 8px;
            font-size: 14px;
        }

        input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e1e8ed;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s ease;
            background: white;
        }

        input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .btn-verify {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 14px 30px;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .btn-verify:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }

        .error-message {
            display: none;
            background: #fee;
            color: #c33;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
        }

        .success-message {
            display: none;
            background: #e6f7e6;
            color: #2d7a2d;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
        }

        .info-box {
            background: #f0f4f8;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            border-left: 4px solid #667eea;
        }

        .info-box p {
            color: #555;
            font-size: 14px;
            line-height: 1.6;
        }

        .spinner {
            display: none;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="saber-header">
            <div class="logo-container">
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
            </div>
            <h1>EPC Partner Portal</h1>
        </div>

        <div class="error-message" id="errorMessage"></div>
        <div class="success-message" id="successMessage">Access granted! Redirecting...</div>

        <form id="verifyForm">
            <div class="form-group">
                <label for="email">Email Address</label>
                <input type="email" id="email" name="email" required placeholder="your.email@company.com">
            </div>

            <div class="form-group">
                <label for="invitationCode">Invitation Code</label>
                <input type="text" id="invitationCode" name="invitationCode" required placeholder="Enter your invitation code">
            </div>

            <button type="submit" class="btn-verify">
                <span id="btnText">Verify Access</span>
                <div class="spinner" id="spinner"></div>
            </button>
        </form>

        <div class="info-box">
            <p>
                <strong>Need assistance?</strong><br>
                Contact your Saber representative if you haven't received your invitation code or are experiencing issues accessing the portal.
            </p>
        </div>
    </div>

    <script>
        document.getElementById('verifyForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const code = document.getElementById('invitationCode').value;
            const errorMsg = document.getElementById('errorMessage');
            const successMsg = document.getElementById('successMessage');
            const btnText = document.getElementById('btnText');
            const spinner = document.getElementById('spinner');
            
            errorMsg.style.display = 'none';
            successMsg.style.display = 'none';
            btnText.style.display = 'none';
            spinner.style.display = 'block';
            
            setTimeout(function() {
                if (code === 'ABCD1234') {
                    sessionStorage.setItem('epcAuthenticated', 'true');
                    sessionStorage.setItem('epcEmail', email);
                    sessionStorage.setItem('epcInviteCode', code);
                    
                    successMsg.style.display = 'block';
                    spinner.style.display = 'none';
                    btnText.style.display = 'inline';
                    
                    setTimeout(function() {
                        window.location.href = 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners/SiteAssets/EPCForm/index.aspx';
                    }, 1500);
                } else {
                    errorMsg.textContent = 'Invalid invitation code. Please check your invitation email.';
                    errorMsg.style.display = 'block';
                    spinner.style.display = 'none';
                    btnText.style.display = 'inline';
                }
            }, 1000);
        });
    </script>
</body>
</html>