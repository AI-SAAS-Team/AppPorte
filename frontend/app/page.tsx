"use client";

import { useEffect, useState } from "react";
import PhotoCapture from "@/components/PhotoCapture";
import DoorGallery from "@/components/DoorGallery";
import ResultView from "@/components/ResultView";
import { DOORS } from "@/lib/doors";

// Par défaut on passe par le proxy interne de Next (/api -> backend), ce qui
// rend l'app accessible via un seul tunnel/déploiement. On peut forcer une URL
// backend absolue avec NEXT_PUBLIC_API_URL si besoin.
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "/api";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [selectedDoor, setSelectedDoor] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resultUrl, setResultUrl] = useState<string | null>(null);

  // Génère / révoque l'URL d'aperçu de la photo locale.
  useEffect(() => {
    if (!file) {
      setPreviewUrl(null);
      return;
    }
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  const doorName =
    DOORS.find((d) => d.id === selectedDoor)?.name ?? "Modèle sélectionné";

  const canGenerate = !!file && !!selectedDoor && !loading;

  async function handleGenerate() {
    if (!file || !selectedDoor) return;
    setLoading(true);
    setError(null);
    setResultUrl(null);

    const form = new FormData();
    form.append("file", file);
    form.append("door_id", selectedDoor);

    try {
      const resp = await fetch(`${API_URL}/generate`, {
        method: "POST",
        body: form,
      });

      if (!resp.ok) {
        let message = `Erreur serveur (${resp.status}).`;
        try {
          const data = await resp.json();
          if (data?.detail) message = data.detail;
        } catch {
          /* réponse non JSON, on garde le message générique */
        }
        throw new Error(message);
      }

      const data = await resp.json();
      if (!data?.image) throw new Error("Réponse inattendue du serveur.");
      setResultUrl(data.image);
    } catch (err) {
      if (err instanceof TypeError) {
        // fetch a échoué (réseau / backend éteint)
        setError(
          "Impossible de joindre le serveur. Vérifiez que le backend FastAPI est bien démarré (port 8000)."
        );
      } else {
        setError(err instanceof Error ? err.message : "Erreur inconnue.");
      }
    } finally {
      setLoading(false);
    }
  }

  function handleReset() {
    setResultUrl(null);
    setError(null);
  }

  return (
    <main className="mx-auto max-w-5xl px-4 py-8 sm:py-12">
      <header className="mb-10 text-center">
        <h1 className="text-3xl font-bold tracking-tight text-stone-900 sm:text-4xl">
          AppDePorte
        </h1>
        <p className="mx-auto mt-3 max-w-xl text-stone-600">
          Photographiez votre porte d&apos;entrée, choisissez un nouveau modèle,
          et visualisez le rendu sur votre façade grâce à l&apos;IA.
        </p>
      </header>

      {resultUrl && previewUrl ? (
        <section className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm sm:p-8">
          <h2 className="mb-5 text-center text-xl font-semibold text-stone-800">
            Votre résultat
          </h2>
          <ResultView
            beforeUrl={previewUrl}
            afterUrl={resultUrl}
            doorName={doorName}
            onReset={handleReset}
          />
        </section>
      ) : (
        <div className="space-y-8">
          {/* Étape 1 : photo */}
          <section className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm sm:p-8">
            <div className="mb-4 flex items-center gap-3">
              <StepBadge n={1} />
              <h2 className="text-lg font-semibold text-stone-800">
                Votre photo
              </h2>
            </div>
            <PhotoCapture
              previewUrl={previewUrl}
              onSelect={(f) => {
                setFile(f);
                setError(null);
              }}
              onClear={() => setFile(null)}
            />
          </section>

          {/* Étape 2 : galerie */}
          <section className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm sm:p-8">
            <div className="mb-4 flex items-center gap-3">
              <StepBadge n={2} />
              <h2 className="text-lg font-semibold text-stone-800">
                Choisissez un modèle de porte
              </h2>
            </div>
            <DoorGallery
              selectedId={selectedDoor}
              onSelect={(id) => {
                setSelectedDoor(id);
                setError(null);
              }}
            />
          </section>

          {/* Étape 3 : génération */}
          <section className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm sm:p-8">
            <div className="mb-4 flex items-center gap-3">
              <StepBadge n={3} />
              <h2 className="text-lg font-semibold text-stone-800">
                Générez le rendu
              </h2>
            </div>

            {error && (
              <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {error}
              </div>
            )}

            <div className="flex flex-col items-center gap-3">
              <button
                onClick={handleGenerate}
                disabled={!canGenerate}
                className="inline-flex items-center gap-2 rounded-lg bg-amber-600 px-8 py-3 text-base font-semibold text-white transition enabled:hover:bg-amber-700 disabled:cursor-not-allowed disabled:bg-stone-300"
              >
                {loading && (
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                )}
                {loading ? "Génération en cours…" : "✨ Générer ma porte"}
              </button>
              {!file && (
                <p className="text-sm text-stone-500">
                  Ajoutez d&apos;abord une photo de votre porte.
                </p>
              )}
              {file && !selectedDoor && (
                <p className="text-sm text-stone-500">
                  Sélectionnez un modèle dans la galerie.
                </p>
              )}
              {loading && (
                <p className="text-sm text-stone-500">
                  Cela peut prendre 10 à 30 secondes.
                </p>
              )}
            </div>
          </section>
        </div>
      )}

      <footer className="mt-12 text-center text-xs text-stone-400">
        Généré par IA — les rendus sont des simulations et peuvent différer du
        produit réel.
      </footer>
    </main>
  );
}

function StepBadge({ n }: { n: number }) {
  return (
    <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-amber-600 text-sm font-bold text-white">
      {n}
    </span>
  );
}
