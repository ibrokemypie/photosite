import React from "react";
import { createRoot } from "react-dom/client";

import Gallery from "./gallery.tsx";

const rootElement = document.getElementById("root");

if (rootElement === null) {
  throw new Error("Need a root element!");
}

const root = createRoot(rootElement);
root.render(
  <React.StrictMode>
    <Gallery />
  </React.StrictMode>,
);
