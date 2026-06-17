"use client";

import { DOORS } from "@/lib/doors";

type Props = {
  selectedId: string | null;
  onSelect: (id: string) => void;
};

export default function DoorGallery({ selectedId, onSelect }: Props) {
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-5">
      {DOORS.map((door) => {
        const selected = door.id === selectedId;
        return (
          <button
            key={door.id}
            onClick={() => onSelect(door.id)}
            aria-pressed={selected}
            className={`group flex flex-col overflow-hidden rounded-xl border-2 bg-white text-left transition ${
              selected
                ? "border-amber-500 ring-2 ring-amber-200"
                : "border-stone-200 hover:border-stone-400"
            }`}
          >
            <div className="relative aspect-[5/7] bg-stone-100">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={door.preview}
                alt={door.name}
                className="h-full w-full object-cover"
              />
              {selected && (
                <span className="absolute right-2 top-2 flex h-6 w-6 items-center justify-center rounded-full bg-amber-500 text-xs font-bold text-white">
                  ✓
                </span>
              )}
            </div>
            <span className="px-2 py-2 text-xs font-medium leading-tight text-stone-700">
              {door.name}
            </span>
          </button>
        );
      })}
    </div>
  );
}
