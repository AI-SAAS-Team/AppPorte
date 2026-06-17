// Catalogue des 15 modèles affichés dans la galerie.
// Les `id` doivent correspondre à ceux du backend (backend/doors.py).
// `preview` pointe vers l'aperçu dans /public/doors/.

export type Door = {
  id: string;
  name: string;
  preview: string;
};

export const DOORS: Door[] = [
  { id: "door-1", name: "Anthracite vitrage latéral", preview: "/doors/door-1.jpg" },
  { id: "door-2", name: "Anthracite à rainures", preview: "/doors/door-2.jpg" },
  { id: "door-3", name: "Blanche lignes horizontales", preview: "/doors/door-3.jpg" },
  { id: "door-4", name: "Rouge bordeaux à panneaux", preview: "/doors/door-4.svg" },
  { id: "door-5", name: "Bleu pastel campagne", preview: "/doors/door-5.svg" },
  { id: "door-6", name: "Aluminium noir design", preview: "/doors/door-6.svg" },
  { id: "door-7", name: "Bois clair scandinave", preview: "/doors/door-7.svg" },
  { id: "door-8", name: "Verte forêt cottage", preview: "/doors/door-8.svg" },
  { id: "door-9", name: "Blanche moderne lisse", preview: "/doors/door-9.svg" },
  { id: "door-10", name: "Acier industriel verrière", preview: "/doors/door-10.svg" },
  { id: "door-11", name: "Noyer foncé à rainures", preview: "/doors/door-11.svg" },
  { id: "door-12", name: "Art déco vitrail", preview: "/doors/door-12.svg" },
  { id: "door-13", name: "Gris béton mat", preview: "/doors/door-13.svg" },
  { id: "door-14", name: "Bois & verre demi-lune", preview: "/doors/door-14.svg" },
  { id: "door-15", name: "Jaune moutarde rétro", preview: "/doors/door-15.svg" },
];
