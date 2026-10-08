/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: [],
  },
  async rewrites() {
    const apiUrl = process.env.API_INTERNAL_URL || "http://localhost:8000"
    return [
      ...["tenants", "users", "monitors", "metrics", "agents"].map((resource) => ({
        source: `/api/v1/${resource}`,
        destination: `${apiUrl}/api/v1/${resource}/`,
      })),
      {
        source: "/api/v1/:path*",
        destination: `${apiUrl}/api/v1/:path*`,
      },
    ]
  },
}

module.exports = nextConfig