// Configuration helper for environment-specific URLs

export function getWorkerUrl() {
  // If explicitly set in environment, use that
  if (process.env.NEXT_PUBLIC_WORKER_URL) {
    return process.env.NEXT_PUBLIC_WORKER_URL;
  }

  // Determine based on current host
  if (typeof window !== 'undefined') {
    const host = window.location.hostname;

    // Production
    if (host === 'epc.saberrenewable.energy') {
      return 'https://epc.saberrenewable.energy';
    }

    // Staging
    if (host === 'staging-epc.saberrenewable.energy') {
      return 'https://staging-epc.saberrenewable.energy';
    }

    // Local development
    if (host === 'localhost' || host === '127.0.0.1') {
      return 'http://localhost:8787';
    }

    // Cloudflare Pages preview deployments (e.g., abc123.saber-epc-portal.pages.dev)
    if (host.endsWith('.pages.dev')) {
      // For preview deployments, use the same domain for API
      // This assumes the Worker is bound to the Pages project
      return `https://${host}`;
    }
  }

  // Server-side or fallback - use relative URLs
  // This will work when the Worker is bound to the same domain
  return '';
}

// Helper to build API URLs
export function getApiUrl(path) {
  const baseUrl = getWorkerUrl();
  // Ensure path starts with /
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;

  // If baseUrl is empty (server-side), return just the path
  // This allows relative URLs to work properly
  if (!baseUrl) {
    return normalizedPath;
  }

  return `${baseUrl}${normalizedPath}`;
}