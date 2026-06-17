/** @type {import('next').NextConfig} */

// URL du backend FastAPI vue depuis le SERVEUR Next (mode proxy, dev/local).
const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000";

// Mode export statique (pour Firebase Hosting / hébergement statique).
// Activé via STATIC_EXPORT=1 (voir le script "build:firebase").
// En export il n'y a pas de serveur Next : pas de proxy /api, le navigateur
// appelle directement le backend (NEXT_PUBLIC_API_URL = URL Railway).
const isExport = process.env.STATIC_EXPORT === "1";

const nextConfig = isExport
  ? {
      reactStrictMode: true,
      output: "export",
      images: { unoptimized: true },
    }
  : {
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
