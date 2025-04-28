/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['localhost', 'api.dains.app'],
  },
  env: {
    API_URL: process.env.API_URL || 'http://localhost:8000',
  },
}

module.exports = nextConfig 