/** @type {import('next').NextConfig} */
const nextConfig = {
    images: {
        domains: ['localhost'],
    },
    async rewrites() {
        return [
            {
                source: '/api/:path*',
                destination: 'http://localhost:8000/api/:path*',
            },
            {
                source: '/uploads/:path*',
                destination: 'http://localhost:8000/uploads/:path*',
            },
        ];
    },
}

module.exports = nextConfig
