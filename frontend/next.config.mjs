/** @type {import('next').NextConfig} */

// URL du backend FastAPI vue depuis le SERVEUR Next (pas le navigateur).
// Le navigateur n'appelle que le frontend (/api/...), qui proxie vers le backend.
// Ça permet d'exposer toute l'app via un seul tunnel sur le port 3000.
const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000";

const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${BACKEND_URL}/:path*`,
      },
    ];
  },
};

export default nextConfig;
