# Next.js Frontend - Technology Guide

> **React-based Frontend Application for EPC Partner Portal**

## 📋 Overview

The EPC Partner Portal frontend is built using Next.js 15.4.4, providing a modern, responsive, and high-performance web application for partner onboarding. The application leverages React's component architecture with Next.js optimizations for production deployment on Cloudflare Pages.

---

## 🏗️ **Application Architecture**

### **Project Structure**
```
epc-portal-react/
├── src/
│   ├── app/                     # Next.js App Router
│   │   ├── globals.css         # Global styles
│   │   ├── layout.tsx          # Root layout component
│   │   ├── page.tsx            # Home page
│   │   ├── form/               # Application form pages
│   │   │   ├── page.tsx        # Form entry point
│   │   │   └── components/     # Form-specific components
│   │   ├── api/                # API routes (Pages Functions)
│   │   │   ├── validate-invitation/
│   │   │   ├── epc-application/
│   │   │   └── upload-file/
│   │   └── invite/             # Invitation validation
│   ├── components/             # Reusable UI components
│   │   ├── ui/                 # Base UI components
│   │   ├── forms/              # Form components
│   │   └── layout/             # Layout components
│   ├── lib/                    # Utility functions
│   │   ├── utils.ts            # General utilities
│   │   ├── api.ts              # API client functions
│   │   └── validation.ts       # Form validation schemas
│   ├── hooks/                  # Custom React hooks
│   │   ├── useAutoSave.ts      # Auto-save functionality
│   │   ├── useFormState.ts     # Form state management
│   │   └── useFileUpload.ts    # File upload handling
│   └── types/                  # TypeScript type definitions
│       ├── application.ts      # Application data types
│       ├── invitation.ts       # Invitation types
│       └── api.ts              # API response types
├── public/                     # Static assets
│   ├── images/                 # Saber branding assets
│   └── favicon.ico             # Site favicon
├── tailwind.config.js          # Tailwind CSS configuration
├── next.config.js              # Next.js configuration
├── package.json                # Dependencies and scripts
└── wrangler.toml              # Cloudflare Pages configuration
```

---

## ⚛️ **React Components**

### **Core Application Components**

#### **ApplicationForm** (Main Form Component)
```typescript
// src/components/forms/ApplicationForm.tsx
import { useState, useEffect } from 'react';
import { useAutoSave } from '@/hooks/useAutoSave';
import { ApplicationData } from '@/types/application';

interface ApplicationFormProps {
  invitationCode: string;
  initialData?: Partial<ApplicationData>;
}

export function ApplicationForm({ invitationCode, initialData }: ApplicationFormProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState<ApplicationData>(initialData || {});

  // Auto-save every 3 seconds
  useAutoSave(formData, invitationCode, currentStep);

  const steps = [
    { number: 1, title: 'Company Information', component: CompanyInfoStep },
    { number: 2, title: 'Contact Details', component: ContactDetailsStep },
    { number: 3, title: 'Capabilities', component: CapabilitiesStep },
    { number: 4, title: 'Roles & Responsibilities', component: RolesStep },
    { number: 5, title: 'Compliance & Insurance', component: ComplianceStep },
    { number: 6, title: 'Agreement & Submission', component: AgreementStep }
  ];

  return (
    <div className="max-w-4xl mx-auto p-6">
      <StepIndicator currentStep={currentStep} totalSteps={steps.length} />

      <form onSubmit={handleSubmit}>
        {steps.map(step => (
          <div key={step.number} className={currentStep === step.number ? 'block' : 'hidden'}>
            <step.component
              data={formData}
              onChange={setFormData}
              onNext={() => setCurrentStep(prev => Math.min(prev + 1, steps.length))}
              onPrevious={() => setCurrentStep(prev => Math.max(prev - 1, 1))}
            />
          </div>
        ))}
      </form>
    </div>
  );
}
```

#### **FileUpload** (Document Upload Component)
```typescript
// src/components/forms/FileUpload.tsx
import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useFileUpload } from '@/hooks/useFileUpload';

interface FileUploadProps {
  invitationCode: string;
  maxFiles?: number;
  acceptedTypes?: string[];
  onUploadComplete?: (files: UploadedFile[]) => void;
}

export function FileUpload({ invitationCode, maxFiles = 5, acceptedTypes, onUploadComplete }: FileUploadProps) {
  const { uploadFile, uploadProgress, uploadError } = useFileUpload(invitationCode);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    for (const file of acceptedFiles) {
      try {
        const result = await uploadFile(file);
        console.log('File uploaded:', result);
      } catch (error) {
        console.error('Upload failed:', error);
      }
    }
  }, [uploadFile]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    maxFiles,
    accept: acceptedTypes?.reduce((acc, type) => ({ ...acc, [type]: [] }), {})
  });

  return (
    <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
      <div {...getRootProps()} className="cursor-pointer">
        <input {...getInputProps()} />
        {isDragActive ? (
          <p className="text-center text-blue-600">Drop files here...</p>
        ) : (
          <div className="text-center">
            <p className="text-gray-600">Drag & drop files here, or click to select</p>
            <p className="text-sm text-gray-400 mt-2">Maximum {maxFiles} files, 10MB each</p>
          </div>
        )}
      </div>

      {uploadProgress > 0 && (
        <div className="mt-4">
          <div className="bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
          <p className="text-sm text-gray-600 mt-1">{uploadProgress}% uploaded</p>
        </div>
      )}

      {uploadError && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-800 text-sm">{uploadError}</p>
        </div>
      )}
    </div>
  );
}
```

---

## 🎣 **Custom React Hooks**

### **useAutoSave** (Automatic Form Saving)
```typescript
// src/hooks/useAutoSave.ts
import { useEffect, useRef } from 'react';
import { debounce } from 'lodash';
import { saveDraft } from '@/lib/api';

export function useAutoSave<T>(data: T, invitationCode: string, step: number) {
  const saveTimeoutRef = useRef<NodeJS.Timeout>();
  const lastSavedRef = useRef<string>('');

  const debouncedSave = useRef(
    debounce(async (dataToSave: T, code: string, stepNumber: number) => {
      try {
        await saveDraft(code, stepNumber, dataToSave);
        console.log('Auto-saved at:', new Date().toLocaleTimeString());
      } catch (error) {
        console.error('Auto-save failed:', error);
      }
    }, 3000)
  ).current;

  useEffect(() => {
    const currentDataString = JSON.stringify(data);

    // Only save if data has actually changed
    if (currentDataString !== lastSavedRef.current && Object.keys(data as object).length > 0) {
      debouncedSave(data, invitationCode, step);
      lastSavedRef.current = currentDataString;
    }
  }, [data, invitationCode, step, debouncedSave]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      debouncedSave.cancel();
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
    };
  }, [debouncedSave]);
}
```

### **useFileUpload** (File Upload Management)
```typescript
// src/hooks/useFileUpload.ts
import { useState, useCallback } from 'react';
import { uploadFileToR2 } from '@/lib/api';

export function useFileUpload(invitationCode: string) {
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const uploadFile = useCallback(async (file: File) => {
    setIsUploading(true);
    setUploadError(null);
    setUploadProgress(0);

    try {
      // Get presigned URL from API
      const { uploadUrl, r2Key } = await fetch('/api/upload-file', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          invitationCode,
          fileName: file.name,
          fileType: file.type,
          fileSize: file.size
        })
      }).then(res => res.json());

      // Upload directly to R2 with progress tracking
      const xhr = new XMLHttpRequest();

      return new Promise((resolve, reject) => {
        xhr.upload.addEventListener('progress', (event) => {
          if (event.lengthComputable) {
            const progress = (event.loaded / event.total) * 100;
            setUploadProgress(Math.round(progress));
          }
        });

        xhr.addEventListener('load', () => {
          if (xhr.status === 200) {
            setUploadProgress(100);
            resolve({ r2Key, fileName: file.name });
          } else {
            reject(new Error(`Upload failed: ${xhr.statusText}`));
          }
        });

        xhr.addEventListener('error', () => {
          reject(new Error('Upload failed: Network error'));
        });

        xhr.open('PUT', uploadUrl);
        xhr.setRequestHeader('Content-Type', file.type);
        xhr.send(file);
      });
    } catch (error) {
      setUploadError(error instanceof Error ? error.message : 'Upload failed');
      throw error;
    } finally {
      setIsUploading(false);
    }
  }, [invitationCode]);

  return {
    uploadFile,
    uploadProgress,
    uploadError,
    isUploading
  };
}
```

---

## 🎨 **Styling & UI Framework**

### **Tailwind CSS Configuration**
```javascript
// tailwind.config.js
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        saber: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          900: '#0c4a6e',
        },
        green: {
          50: '#f0fdf4',
          500: '#22c55e',
          600: '#16a34a',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
```

### **Component Design System**
```typescript
// src/components/ui/Button.tsx
import { ButtonHTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', loading, children, disabled, ...props }, ref) => {
    const baseClasses = 'inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50';

    const variants = {
      primary: 'bg-saber-600 text-white hover:bg-saber-700 focus-visible:ring-saber-600',
      secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200 focus-visible:ring-gray-500',
      outline: 'border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 focus-visible:ring-gray-500',
      ghost: 'text-gray-700 hover:bg-gray-100 focus-visible:ring-gray-500'
    };

    const sizes = {
      sm: 'h-8 px-3 text-sm',
      md: 'h-10 px-4 text-sm',
      lg: 'h-12 px-6 text-base'
    };

    return (
      <button
        className={cn(baseClasses, variants[variant], sizes[size], className)}
        disabled={disabled || loading}
        ref={ref}
        {...props}
      >
        {loading && (
          <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" className="opacity-25" />
            <path fill="currentColor" className="opacity-75" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
        )}
        {children}
      </button>
    );
  }
);
```

---

## 🔧 **Next.js Configuration**

### **next.config.js**
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Cloudflare Pages optimization
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  },

  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://epc.saberrenewable.energy',
    NEXT_PUBLIC_CLOUDFLARE_ACCOUNT_ID: process.env.CLOUDFLARE_ACCOUNT_ID,
  },

  // Webpack configuration for Cloudflare Workers compatibility
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      };
    }
    return config;
  },

  // Experimental features for performance
  experimental: {
    optimizeCss: true,
    esmExternals: true,
  },

  // Redirects for legacy URLs
  async redirects() {
    return [
      {
        source: '/apply',
        destination: '/form',
        permanent: true,
      },
    ];
  },
};

module.exports = nextConfig;
```

### **wrangler.toml** (Cloudflare Pages Configuration)
```toml
name = "saber-epc-portal"
compatibility_date = "2024-09-17"

[env.production]
name = "saber-epc-portal"
route = "epc.saberrenewable.energy/*"

[env.production.vars]
NEXT_PUBLIC_API_URL = "https://epc.saberrenewable.energy"
ENVIRONMENT = "production"

[[env.production.d1_databases]]
binding = "DB"
database_name = "epc_form_data"
database_id = "your-d1-database-id"

[[env.production.r2_buckets]]
binding = "STORAGE"
bucket_name = "epc-file-uploads"

[build]
command = "npm run build"
destination = "out"

[env.staging]
name = "saber-epc-portal-staging"
```

---

## 📊 **Performance Optimization**

### **Code Splitting & Lazy Loading**
```typescript
// Dynamic imports for heavy components
import dynamic from 'next/dynamic';

const FileUpload = dynamic(() => import('@/components/forms/FileUpload'), {
  loading: () => <div className="animate-pulse bg-gray-200 h-32 rounded-lg" />,
  ssr: false
});

const PDFViewer = dynamic(() => import('@/components/PDFViewer'), {
  loading: () => <div>Loading PDF viewer...</div>,
  ssr: false
});
```

### **Image Optimization**
```typescript
// src/components/SaberLogo.tsx
import Image from 'next/image';

export function SaberLogo({ className }: { className?: string }) {
  return (
    <Image
      src="/images/saber-logo.svg"
      alt="Saber Renewables"
      width={200}
      height={60}
      priority
      className={className}
    />
  );
}
```

### **Bundle Analysis**
```json
// package.json scripts
{
  "scripts": {
    "analyze": "cross-env ANALYZE=true npm run build",
    "build": "next build",
    "dev": "next dev",
    "start": "next start"
  }
}
```

---

## 🔍 **Testing Strategy**

### **Component Testing with Jest**
```typescript
// src/components/__tests__/ApplicationForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ApplicationForm } from '@/components/forms/ApplicationForm';

describe('ApplicationForm', () => {
  test('renders first step correctly', () => {
    render(<ApplicationForm invitationCode="TEST1234" />);

    expect(screen.getByText('Company Information')).toBeInTheDocument();
    expect(screen.getByRole('textbox', { name: /company name/i })).toBeInTheDocument();
  });

  test('auto-saves form data', async () => {
    const saveDraftSpy = jest.spyOn(require('@/lib/api'), 'saveDraft');

    render(<ApplicationForm invitationCode="TEST1234" />);

    const companyNameInput = screen.getByRole('textbox', { name: /company name/i });
    fireEvent.change(companyNameInput, { target: { value: 'Test Company' } });

    await waitFor(() => {
      expect(saveDraftSpy).toHaveBeenCalledWith('TEST1234', 1, expect.any(Object));
    }, { timeout: 4000 });
  });
});
```

### **End-to-End Testing with Playwright**
```typescript
// e2e/application-flow.spec.ts
import { test, expect } from '@playwright/test';

test('complete application submission flow', async ({ page }) => {
  await page.goto('/form?invitationCode=TEST1234');

  // Step 1: Company Information
  await page.fill('[name="companyName"]', 'Test EPC Company');
  await page.fill('[name="companyRegistration"]', '12345678');
  await page.click('button:has-text("Next")');

  // Step 2: Contact Details
  await page.fill('[name="primaryContactName"]', 'John Doe');
  await page.fill('[name="primaryContactEmail"]', 'john@testepc.com');
  await page.click('button:has-text("Next")');

  // Continue through all steps...

  // Final submission
  await page.check('[name="termsAccepted"]');
  await page.click('button:has-text("Submit Application")');

  await expect(page.locator('text=Application submitted successfully')).toBeVisible();
});
```

---

## 🚀 **Deployment Process**

### **Build Script**
```bash
#!/bin/bash
# deploy-frontend.sh

echo "Building Next.js application for Cloudflare Pages..."

# Install dependencies
npm ci

# Run tests
npm run test

# Build for production
npm run build

# Generate static files
npm run export

echo "Build complete. Ready for Cloudflare Pages deployment."
```

### **CI/CD with GitHub Actions**
```yaml
# .github/workflows/deploy.yml
name: Deploy to Cloudflare Pages

on:
  push:
    branches: [main]
    paths: ['epc-portal-react/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: epc-portal-react/package-lock.json

      - name: Install dependencies
        run: npm ci
        working-directory: epc-portal-react

      - name: Run tests
        run: npm run test:ci
        working-directory: epc-portal-react

      - name: Build application
        run: npm run build
        working-directory: epc-portal-react
        env:
          NEXT_PUBLIC_API_URL: https://epc.saberrenewable.energy

      - name: Deploy to Cloudflare Pages
        uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: saber-epc-portal
          directory: epc-portal-react/out
```

---

## 🔮 **Future Enhancements**

### **Progressive Web App (PWA)**
```typescript
// next.config.js - PWA configuration
const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
});

module.exports = withPWA({
  // existing config
});
```

### **Advanced Features Roadmap**
- **Real-time Collaboration**: WebSocket integration for live form editing
- **Offline Support**: Service worker for offline form completion
- **Advanced Validation**: Real-time field validation with instant feedback
- **Accessibility Enhancements**: WCAG 2.1 AA compliance
- **Internationalization**: Multi-language support for global partners

---

**Document Version**: 1.0
**Last Updated**: September 17, 2025
**Next Review**: December 1, 2025
**Owner**: Saber Renewables Frontend Development Team