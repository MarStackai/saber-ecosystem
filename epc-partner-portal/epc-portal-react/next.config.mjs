import withMarkdoc from '@markdoc/next.js'
import withSearch from './src/markdoc/search.mjs'

if (!process.env.NEXT_FORCE_WASM_BINARY) {
  process.env.NEXT_FORCE_WASM_BINARY = '1'
}

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Produce a static export for Cloudflare Pages; dynamic APIs are served via /functions
  output: 'export',
  images: {
    // Required for static export when using next/image
    unoptimized: true,
  },
  experimental: {
    useWasmBinary: true,
  },
  pageExtensions: ['js', 'jsx', 'md', 'ts', 'tsx'],
  async rewrites() {
    // In dev, proxy Next API calls to the local Pages Functions dev server
    const base = process.env.NEXT_PUBLIC_API_URL
    if (!base) return []
    return [
      {
        source: '/api/:path*',
        destination: `${base}/api/:path*`,
      },
    ]
  },
  webpack: (config, { isServer, webpack }) => {
    if (isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        async_hooks: false,
        // Add a fallback for the 'File' API on the server
        File: false,
      }
    }
    return config
  },
}

// Temporarily disable search to test build
// export default withSearch(
//   withMarkdoc({ schemaPath: './src/markdoc' })(nextConfig),
// )
export default withMarkdoc({ schemaPath: './src/markdoc' })(nextConfig)
