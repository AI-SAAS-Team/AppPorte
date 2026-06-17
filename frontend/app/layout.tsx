import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AppDePorte — Visualisez votre nouvelle porte d'entrée",
  description:
    "Prenez une photo de votre porte d'entrée, choisissez un modèle et laissez l'IA générer le rendu sur votre façade.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr">
      <body>{children}</body>
    </html>
  );
}
