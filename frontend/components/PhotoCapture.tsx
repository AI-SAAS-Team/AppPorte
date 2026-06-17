"use client";

import { useCallback, useRef, useState } from "react";

type Props = {
  previewUrl: string | null;
  onSelect: (file: File) => void;
  onClear: () => void;
};

const ACCEPTED = ["image/jpeg", "image/png", "image/webp"];

export default function PhotoCapture({ previewUrl, onSelect, onClear }: Props) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  const handleFiles = useCallback(
    (files: FileList | null) => {
      setLocalError(null);
      const file = files?.[0];
      if (!file) return;
      if (!ACCEPTED.includes(file.type)) {
        setLocalError("Format non supporté. Choisissez une image JPEG, PNG ou WebP.");
        return;
      }
      if (file.size > 50 * 1024 * 1024) {
        setLocalError("Image trop lourde (max 50 Mo).");
        return;
      }
      onSelect(file);
    },
    [onSelect]
  );

  return (
    <div>
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
      />
      <input
        ref={cameraInputRef}
        type="file"
        accept="image/*"
        capture="environment"
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
      />

      {previewUrl ? (
        <div className="relative overflow-hidden rounded-xl border border-stone-300 bg-stone-100">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={previewUrl}
            alt="Votre porte d'entrée"
            className="max-h-[420px] w-full object-contain"
          />
          <button
            onClick={onClear}
            className="absolute right-3 top-3 rounded-full bg-black/60 px-3 py-1 text-sm font-medium text-white backdrop-blur transition hover:bg-black/80"
          >
            Changer
          </button>
        </div>
      ) : (
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragOver(false);
            handleFiles(e.dataTransfer.files);
          }}
          className={`flex flex-col items-center justify-center rounded-xl border-2 border-dashed px-6 py-12 text-center transition ${
            dragOver
              ? "border-amber-500 bg-amber-50"
              : "border-stone-300 bg-stone-50"
          }`}
        >
          <svg
            className="mb-3 h-12 w-12 text-stone-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={1.5}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M3 16.5V18a2.25 2.25 0 002.25 2.25h13.5A2.25 2.25 0 0021 18v-1.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"
            />
          </svg>
          <p className="mb-4 text-sm text-stone-600">
            Glissez une photo ici, ou
          </p>
          <div className="flex flex-wrap items-center justify-center gap-3">
            <button
              onClick={() => fileInputRef.current?.click()}
              className="rounded-lg bg-stone-800 px-5 py-2.5 text-sm font-medium text-white transition hover:bg-stone-700"
            >
              Choisir un fichier
            </button>
            <button
              onClick={() => cameraInputRef.current?.click()}
              className="rounded-lg border border-stone-300 bg-white px-5 py-2.5 text-sm font-medium text-stone-800 transition hover:bg-stone-100"
            >
              📷 Prendre une photo
            </button>
          </div>
        </div>
      )}

      {localError && (
        <p className="mt-3 text-sm text-red-600">{localError}</p>
      )}
    </div>
  );
}
