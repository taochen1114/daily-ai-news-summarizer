/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['localhost', 'api.dains.app'],
  },
  env: {
    NEXT_PUBLIC_API_URL:
      process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    NEXT_PUBLIC_SITE_NAME: process.env.NEXT_PUBLIC_SITE_NAME || 'DAINS',
    NEXT_PUBLIC_SITE_DESCRIPTION:
      process.env.NEXT_PUBLIC_SITE_DESCRIPTION || '每日AI新聞與論文摘要',
    NEXT_PUBLIC_SUPABASE_STORAGE_URL:
      'https://lqozyncypoyfxhyannqb.supabase.co/storage/v1/object/public/ai-news-storage',
  },
};

module.exports = nextConfig;
