"use client";

import { useCallback, useEffect, useRef, useState } from "react";

type Props = {
  beforeUrl: string;
  afterUrl: string;
  doorName: string;
  onReset: () => void;
};

type Mode = "slider" | "side";

export default function ResultView({
  beforeUrl,
  afterUrl,
  doorName,
  onReset,
}: Props) {
  const [pos, setPos] = useState(50); // position du curseur (%)
  const [mode, setMode] = useState<Mode>("slider");
  const containerRef = useRef<HTMLDivElement>(null);
  const dragging = useRef(false);

  const updateFromClientX = useCallback((clientX: number) => {
    const el = containerRef.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const ratio = ((clientX - rect.left) / rect.width) * 100;
    setPos(Math.max(0, Math.min(100, ratio)));
  }, []);

  // Glisser : on écoute au niveau du document pour ne pas "perdre" le curseur.
  useEffect(() => {
    if (mode !== "slider") return;
    const move = (e: MouseEvent) =>
      dragging.current && updateFromClientX(e.clientX);
    const touch = (e: TouchEvent) =>
      dragging.current && updateFromClientX(e.touches[0].clientX);
    const stop = () => (dragging.current = false);
    window.addEventListener("mousemove", move);
    window.addEventListener("mouseup", stop);
    window.addEventListener("touchmove", touch, { passive: true });
    window.addEventListener("touchend", stop);
    return () => {
      window.removeEventListener("mousemove", move);
      window.removeEventListener("mouseup", stop);
      window.removeEventListener("touchmove", touch);
      window.removeEventListener("touchend", stop);
    };
  }, [mode, updateFromClientX]);

  const downloadName = `porte-${doorName
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "")}.png`;

  return (
    <div>
      {/* Sélecteur de mode d'affichage */}
      <div className="mb-4 flex justify-center">
        <div className="inline-flex rounded-lg border border-stone-200 bg-stone-100 p-1 text-sm">
          <button
            onClick={() => setMode("slider")}
            className={`rounded-md px-4 py-1.5 font-medium transition ${
              mode === "slider"
                ? "bg-white text-stone-900 shadow-sm"
                : "text-stone-500 hover:text-stone-700"
            }`}
          >
            Comparateur
          </button>
          <button
            onClick={() => setMode("side")}
            className={`rounded-md px-4 py-1.5 font-medium transition ${
              mode === "side"
                ? "bg-white text-stone-900 shadow-sm"
                : "text-stone-500 hover:text-stone-700"
            }`}
          >
            Côte à côte
          </button>
        </div>
      </div>

      {mode === "slider" ? (
        <div
          ref={containerRef}
          className="relative mx-auto w-fit cursor-ew-resize select-none overflow-hidden rounded-xl border border-stone-300 bg-stone-100"
          onMouseDown={(e) => {
            dragging.current = true;
            updateFromClientX(e.clientX);
          }}
          onTouchStart={(e) => {
            dragging.current = true;
            updateFromClientX(e.touches[0].clientX);
          }}
        >
          {/* L'image APRÈS définit la taille du cadre */}
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={afterUrl}
            alt="Résultat avec la nouvelle porte"
            className="block max-h-[540px] w-auto select-none"
            draggable={false}
          />
          {/* L'image AVANT, superposée pile dessus et découpée par clip-path
              (aucune déformation : on masque, on ne redimensionne pas) */}
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={beforeUrl}
            alt="Porte d'origine"
            className="absolute inset-0 block h-full w-full select-none object-cover"
            style={{ clipPath: `inset(0 ${100 - pos}% 0 0)` }}
            draggable={false}
          />

          {/* Étiquettes */}
          <span className="pointer-events-none absolute left-3 top-3 rounded bg-black/65 px-2 py-1 text-xs font-medium text-white">
            Avant
          </span>
          <span className="pointer-events-none absolute right-3 top-3 rounded bg-amber-500 px-2 py-1 text-xs font-medium text-white">
            Après
          </span>

          {/* Ligne + poignée du curseur */}
          <div
            className="pointer-events-none absolute bottom-0 top-0 w-0.5 -translate-x-1/2 bg-white shadow-[0_0_4px_rgba(0,0,0,0.4)]"
            style={{ left: `${pos}%` }}
          >
            <span className="absolute top-1/2 left-1/2 flex h-9 w-9 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full bg-white text-stone-700 shadow-md">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                <path
                  d="M9 6l-4 6 4 6M15 6l4 6-4 6"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </span>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <figure className="overflow-hidden rounded-xl border border-stone-300 bg-stone-100">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={beforeUrl}
              alt="Porte d'origine"
              className="block max-h-[480px] w-full object-contain"
            />
            <figcaption className="border-t border-stone-200 bg-white px-3 py-2 text-center text-sm font-medium text-stone-600">
              Avant
            </figcaption>
          </figure>
          <figure className="overflow-hidden rounded-xl border border-amber-300 bg-stone-100">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={afterUrl}
              alt="Résultat avec la nouvelle porte"
              className="block max-h-[480px] w-full object-contain"
            />
            <figcaption className="border-t border-amber-200 bg-amber-50 px-3 py-2 text-center text-sm font-medium text-amber-700">
              Après — {doorName}
            </figcaption>
          </figure>
        </div>
      )}

      {mode === "slider" && (
        <p className="mt-3 text-center text-sm text-stone-600">
          Glissez le curseur pour comparer — modèle&nbsp;:{" "}
          <span className="font-medium text-stone-800">{doorName}</span>
        </p>
      )}

      <div className="mt-5 flex flex-wrap justify-center gap-3">
        <a
          href={afterUrl}
          download={downloadName}
          className="rounded-lg bg-amber-600 px-6 py-2.5 text-sm font-medium text-white transition hover:bg-amber-700"
        >
          ⬇ Télécharger le résultat
        </a>
        <button
          onClick={onReset}
          className="rounded-lg border border-stone-300 bg-white px-6 py-2.5 text-sm font-medium text-stone-800 transition hover:bg-stone-100"
        >
          Recommencer
        </button>
      </div>
    </div>
  );
}
