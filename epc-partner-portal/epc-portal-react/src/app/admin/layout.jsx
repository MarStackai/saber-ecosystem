'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

const navigation = [
  {
    name: 'Dashboard',
    href: '/admin',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2v0" />
      </svg>
    ),
  },
  {
    name: 'Partners',
    href: '/admin/partners',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
    ),
    children: [
      { name: 'Applications', href: '/admin/partners/applications' },
      { name: 'Approved Partners', href: '/admin/partners/approved' },
      { name: 'Analytics', href: '/admin/partners/analytics' },
    ],
  },
  {
    name: 'Tenders',
    href: '/admin/tenders',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
      </svg>
    ),
    children: [
      { name: 'Active Tenders', href: '/admin/tenders' },
      { name: 'Create Tender', href: '/admin/tenders/new' },
      { name: 'Analytics', href: '/admin/tenders/analytics' },
    ],
  },
  {
    name: 'Documents',
    href: '/admin/documents',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2v0" />
      </svg>
    ),
  },
]

export default function OperationsLayout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const pathname = usePathname()

  // Debug: Log when component mounts
  useEffect(() => {
    console.log('Admin layout mounted, pathname:', pathname)
  }, [])

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Mobile sidebar */}
      <div className={`fixed inset-0 z-50 lg:hidden ${sidebarOpen ? '' : 'pointer-events-none'}`}>
        <div
          className={`fixed inset-0 bg-slate-900/80 transition-opacity ${
            sidebarOpen ? 'opacity-100' : 'opacity-0'
          }`}
          onClick={() => setSidebarOpen(false)}
        />
        <div
          className={`fixed inset-y-0 left-0 w-64 bg-slate-800 transition-transform ${
            sidebarOpen ? 'translate-x-0' : '-translate-x-full'
          }`}
        >
          <div className="flex h-16 items-center justify-between px-6 border-b border-slate-700">
            <div className="flex items-center space-x-3">
              <svg viewBox="0 0 173.11 101.48" className="h-8 w-auto" aria-hidden="true">
                <g>
                  <path fill="#ffffff" d="M65.11,24.31c-14.5-8.51-33.11-3.47-41.62,11.04-8.51,14.5-3.47,33.11,11.04,41.62,11.98,6.94,27.12,5.05,36.89-4.73l38.15-38.15c8.2-6.62,19.86-6.62,28.06.32l-51.71,51.71c-19.86,19.55-51.71,19.55-71.26,0-19.55-19.86-19.55-51.71,0-71.26C31.69-2.8,59.44-5.01,79.3,9.81l-14.5,14.5h.32Z"/>
                  <path fill="#7dbf61" d="M107.36,76.65c14.5,8.51,33.11,3.47,41.62-11.04,8.51-14.5,3.47-33.11-11.04-41.62-11.98-6.94-27.12-5.05-36.89,4.73l-38.15,38.15c-8.2,6.62-19.86,6.62-28.06-.32L87.18,14.85c19.86-19.55,51.71-19.55,71.26,0,19.55,19.86,19.55,51.71,0,71.26-19.55,19.55-45.41,19.55-65.27,5.05l14.5-14.5h-.32Z"/>
                </g>
              </svg>
              <div>
                <div className="text-white font-semibold text-sm">Admin</div>
                <div className="text-slate-400 text-xs">Portal</div>
              </div>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="text-slate-400 hover:text-white"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <nav className="mt-5 px-2">
            {navigation.map((item) => (
              <div key={item.name}>
                <Link
                  href={item.href}
                  className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                    pathname === item.href
                      ? 'bg-slate-700 text-white'
                      : 'text-slate-300 hover:bg-slate-700 hover:text-white'
                  }`}
                >
                  {item.icon}
                  <span className="ml-3">{item.name}</span>
                </Link>
                {item.children && (
                  <div className="ml-6 mt-1 space-y-1">
                    {item.children.map((child) => (
                      <Link
                        key={child.name}
                        href={child.href}
                        className={`group flex items-center px-2 py-1 text-xs rounded-md ${
                          pathname === child.href
                            ? 'bg-slate-600 text-white'
                            : 'text-slate-400 hover:bg-slate-600 hover:text-white'
                        }`}
                      >
                        {child.name}
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </nav>
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-72 lg:flex-col">
        <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-slate-800 px-6">
          <div className="flex h-16 shrink-0 items-center border-b border-slate-700">
            <div className="flex items-center space-x-3">
              <svg viewBox="0 0 173.11 101.48" className="h-8 w-auto" aria-hidden="true">
                <g>
                  <path fill="#ffffff" d="M65.11,24.31c-14.5-8.51-33.11-3.47-41.62,11.04-8.51,14.5-3.47,33.11,11.04,41.62,11.98,6.94,27.12,5.05,36.89-4.73l38.15-38.15c8.2-6.62,19.86-6.62,28.06.32l-51.71,51.71c-19.86,19.55-51.71,19.55-71.26,0-19.55-19.86-19.55-51.71,0-71.26C31.69-2.8,59.44-5.01,79.3,9.81l-14.5,14.5h.32Z"/>
                  <path fill="#7dbf61" d="M107.36,76.65c14.5,8.51,33.11,3.47,41.62-11.04,8.51-14.5,3.47-33.11-11.04-41.62-11.98-6.94-27.12-5.05-36.89,4.73l-38.15,38.15c-8.2,6.62-19.86,6.62-28.06-.32L87.18,14.85c19.86-19.55,51.71-19.55,71.26,0,19.55,19.86,19.55,51.71,0,71.26-19.55,19.55-45.41,19.55-65.27,5.05l14.5-14.5h-.32Z"/>
                </g>
              </svg>
              <div>
                <div className="text-white font-semibold">Admin Portal</div>
                <div className="text-slate-400 text-sm">EPC Management Console</div>
              </div>
            </div>
          </div>
          <nav className="flex flex-1 flex-col">
            <ul role="list" className="flex flex-1 flex-col gap-y-7">
              <li>
                <ul role="list" className="-mx-2 space-y-1">
                  {navigation.map((item) => (
                    <li key={item.name}>
                      <Link
                        href={item.href}
                        className={`group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold ${
                          pathname === item.href
                            ? 'bg-slate-700 text-white'
                            : 'text-slate-300 hover:text-white hover:bg-slate-700'
                        }`}
                      >
                        {item.icon}
                        {item.name}
                      </Link>
                      {item.children && (
                        <ul className="mt-1 ml-6 space-y-1">
                          {item.children.map((child) => (
                            <li key={child.name}>
                              <Link
                                href={child.href}
                                className={`block rounded-md py-1 pr-2 pl-2 text-sm leading-6 ${
                                  pathname === child.href
                                    ? 'bg-slate-600 text-white'
                                    : 'text-slate-400 hover:text-white hover:bg-slate-600'
                                }`}
                              >
                                {child.name}
                              </Link>
                            </li>
                          ))}
                        </ul>
                      )}
                    </li>
                  ))}
                </ul>
              </li>
            </ul>
          </nav>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-72">
        {/* Top bar */}
        <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-slate-700 bg-slate-800 px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8">
          <button
            type="button"
            className="-m-2.5 p-2.5 text-slate-400 lg:hidden"
            onClick={() => {
              console.log('Mobile menu button clicked')
              setSidebarOpen(true)
            }}
          >
            <span className="sr-only">Open sidebar</span>
            <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          {/* Separator */}
          <div className="h-6 w-px bg-slate-600 lg:hidden" />

          <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
            <div className="flex items-center gap-x-4 lg:gap-x-6">
              <div className="hidden lg:block lg:h-6 lg:w-px lg:bg-slate-600" />
              {/* Admin Navigation Links */}
              <nav className="hidden md:flex items-center gap-x-6">
                <Link
                  href="/admin/tenders"
                  className={`text-sm font-medium ${
                    pathname.includes('/admin/tenders') ? 'text-white' : 'text-slate-300 hover:text-white'
                  } transition-colors`}
                >
                  Tenders
                </Link>
                <Link
                  href="/admin/documents"
                  className={`text-sm font-medium ${
                    pathname === '/admin/documents' ? 'text-white' : 'text-slate-300 hover:text-white'
                  } transition-colors`}
                >
                  Documents
                </Link>
                <Link
                  href="/admin/partners"
                  className={`text-sm font-medium ${
                    pathname.includes('/admin/partners') ? 'text-white' : 'text-slate-300 hover:text-white'
                  } transition-colors`}
                >
                  Partners
                </Link>
              </nav>
            </div>
            <div className="flex items-center gap-x-4 lg:gap-x-6 ml-auto">
              <span className="text-sm text-slate-300">operations@saberrenewables.com</span>
              <Link
                href="/"
                className="inline-flex items-center px-3 py-2 border border-slate-600 rounded-md text-sm text-slate-300 hover:text-white hover:border-slate-500"
              >
                <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
                Public Portal
              </Link>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="py-8">
          <div className="px-4 sm:px-6 lg:px-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}