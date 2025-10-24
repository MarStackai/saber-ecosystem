'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import clsx from 'clsx'
import Image from 'next/image'

import saberLogo from '@/images/Saber-logo-wob-green.svg'

function Header() {
  let [isScrolled, setIsScrolled] = useState(false)
  const pathname = usePathname()
  const isFormPage = pathname === '/form'

  useEffect(() => {
    function onScroll() {
      setIsScrolled(window.scrollY > 0)
    }
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => {
      window.removeEventListener('scroll', onScroll)
    }
  }, [])

  return (
    <header
      className={clsx(
        'sticky top-0 z-50 flex flex-none flex-wrap items-center justify-between px-4 py-4 transition duration-500 sm:px-6 lg:px-8',
        isScrolled
          ? 'bg-slate-900/95 backdrop-blur-sm shadow-lg shadow-slate-900/25'
          : 'bg-slate-900/80 backdrop-blur-sm',
      )}
    >
      <div className="flex items-center">
        <Link href="/" aria-label="Saber Renewables Home">
          <Image
            src={saberLogo}
            alt="Saber Renewables"
            className="h-8 w-auto sm:h-10"
            priority
          />
        </Link>
      </div>
      
      <nav className="hidden sm:flex items-center space-x-8">
        {isFormPage ? (
          // Only show Partner Information button on form page
          <Link 
            href="https://saberrenewables.com/partnerships-in-actions/" 
            target="_blank"
            className="rounded-full px-4 py-2 text-sm font-semibold text-white transition-colors hover:opacity-90"
            style={{ backgroundColor: '#7CC061' }}
          >
            Partner Information
          </Link>
        ) : (
          // Show all buttons on other pages
          <>
            <Link 
              href="https://saberrenewables.com/partnerships-in-actions/" 
              target="_blank"
              className="text-slate-300 hover:text-white transition-colors"
            >
              More Information
            </Link>
            <Link 
              href="https://saberrenewables.com/partner-with-us/" 
              target="_blank"
              className="text-slate-300 hover:text-white transition-colors"
            >
              Become a Partner
            </Link>
            <Link
              href="/apply"
              className="rounded-full px-4 py-2 text-sm font-semibold text-white transition-colors hover:opacity-90"
              style={{ backgroundColor: '#7CC061' }}
            >
              Submit Application
            </Link>
          </>
        )}
      </nav>
    </header>
  )
}

export function SaberLayout({ children }) {
  return (
    <div className="min-h-full bg-slate-900">
      <Header />
      <main className="flex-1">
        {children}
      </main>
      
    </div>

  )
}
