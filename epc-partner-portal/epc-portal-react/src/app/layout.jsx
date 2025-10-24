import { Inter } from 'next/font/google'
import localFont from 'next/font/local'
import clsx from 'clsx'

import { Providers } from '@/app/providers'
import { SaberLayout } from '@/components/SaberLayout'

import '@/styles/tailwind.css'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
})

// Use local version of Lexend so that we can use OpenType features
const lexend = localFont({
  src: '../fonts/lexend.woff2',
  display: 'swap',
  variable: '--font-lexend',
})

export const metadata = {
  title: {
    template: '%s - Saber EPC Portal',
    default: 'EPC Partner Portal - Saber Renewables',
  },
  description:
    `Saber Renewable Energy is driving the transition to sustainable energy through innovative solutions, bespoke funding models like our Blended PPA, and a commitment to excellence. Our success is amplified by strong, collaborative partnerships. If you are a forward-thinking supplier, installer, developer, funder, consultant, or strategic introducer who shares our passion for quality and sustainability, we invite you to explore partnership opportunities with us.`,
}

export default function RootLayout({ children }) {
  return (
    <html
      lang="en"
      className={clsx('h-full antialiased', inter.variable, lexend.variable)}
      suppressHydrationWarning
    >
      <body className="min-h-full bg-slate-900 text-white antialiased">
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}
