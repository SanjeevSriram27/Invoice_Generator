/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
  },

  // Production optimizations
  compress: true,
  poweredByHeader: false, // Remove X-Powered-By header

  // Enable experimental optimizations
  experimental: {
    optimizePackageImports: ['@/components', '@/lib', 'react-hot-toast'],
  },

  // Optimize images
  images: {
    formats: ['image/avif', 'image/webp'],
    minimumCacheTTL: 60,
  },

  // Enable SWC minification for faster builds
  swcMinify: true,
}

module.exports = nextConfig
