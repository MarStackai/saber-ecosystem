import Link from 'next/link'
import { CheckCircleIcon } from '@heroicons/react/24/solid'

export default function SuccessPage() {
  return (
    <div className="min-h-[calc(100vh-200px)] flex items-center justify-center px-4 sm:px-6 lg:px-8">
      <div className="max-w-lg w-full space-y-8">
        {/* Glass card effect */}
        <div className="relative">
          <div className="absolute inset-0 rounded-2xl bg-gradient-to-tr from-green-300/20 via-green-300/10 to-blue-300/20 opacity-30 blur-lg" />
          <div className="relative rounded-2xl bg-slate-800/80 ring-1 ring-white/10 backdrop-blur-sm p-8 text-center">
            <div className="absolute -top-px right-11 left-20 h-px bg-gradient-to-r from-green-300/0 via-green-300/40 to-green-300/0" />
            <div className="absolute right-20 -bottom-px left-11 h-px bg-gradient-to-r from-blue-400/0 via-blue-400/40 to-blue-400/0" />
            
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-green-500/20">
              <CheckCircleIcon className="h-8 w-8 text-green-400" />
            </div>
            
            <div className="mt-6">
              <h2 className="text-2xl font-bold tracking-tight text-white">
                Application Submitted Successfully!
              </h2>
              <p className="mt-4 text-slate-400">
                Thank you for your interest in becoming a Saber Renewables EPC partner. 
                We&apos;ve received your application and will review it shortly.
              </p>
            </div>
            
            <div className="mt-8 space-y-4">
              <div className="rounded-lg bg-slate-700/30 p-4 text-left">
                <h3 className="font-medium text-white mb-2">What happens next?</h3>
                <ul className="space-y-2 text-sm text-slate-300">
                  <li className="flex items-start gap-2">
                    <div className="h-1.5 w-1.5 rounded-full bg-green-400 mt-2 flex-shrink-0" />
                    Our team will review your application within 2-3 business days
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="h-1.5 w-1.5 rounded-full bg-green-400 mt-2 flex-shrink-0" />
                    We&apos;ll contact you to discuss the next steps
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="h-1.5 w-1.5 rounded-full bg-green-400 mt-2 flex-shrink-0" />
                    Successful applicants will receive their partner onboarding materials
                  </li>
                </ul>
              </div>
            </div>
            
            <div className="mt-8">
              <Link 
                href="/" 
                className="inline-flex items-center px-6 py-3 text-sm font-semibold text-white bg-green-600 rounded-lg hover:bg-green-500 focus:outline-none focus:ring-2 focus:ring-green-500/50 transition-colors"
              >
                Return Home
              </Link>
            </div>
            
            <div className="mt-6">
              <p className="text-xs text-slate-400">
                Questions? Contact us at{' '}
                <a 
                  href="mailto:partners@saberrenewables.com" 
                  className="text-green-400 hover:text-green-300 transition-colors"
                >
                  partners@saberrenewables.com
                </a>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}