// Catalogue des 15 modèles affichés dans la galerie.
// Les `id` doivent correspondre à ceux du backend (backend/doors.py).
// `preview` pointe vers l'aperçu dans /public/doors/.

export type Door = {
  id: string;
  name: string;
  preview: string;
};

export const DOORS: Door[] = [
  { id: "door-1", name: "Gris vitrage dépoli lignes", preview: "/doors/door-1.png" },
  { id: "door-2", name: "Gris rainures bandes verticales", preview: "/doors/door-2.png" },
  { id: "door-3", name: "Noire bandes vitrées", preview: "/doors/door-3.jpg" },
  { id: "door-4", name: "Anthracite vitrage diagonal", preview: "/doors/door-4.jpg" },
  { id: "door-5", name: "Anthracite perforé barre", preview: "/doors/door-5.jpg" },
  { id: "door-6", name: "Chêne clair vitrage vertical", preview: "/doors/door-6.jpg" },
  { id: "door-7", name: "Anthracite vitrage horizontal", preview: "/doors/door-7.jpg" },
  { id: "door-8", name: "Noyer foncé vitré inox", preview: "/doors/door-8.jpg" },
  { id: "door-9", name: "Aluminium gris & beige", preview: "/doors/door-9.jpg" },
  { id: "door-10", name: "Anthracite impostes vitrées", preview: "/doors/door-10.jpg" },
];
