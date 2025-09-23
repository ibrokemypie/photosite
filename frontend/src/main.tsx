import React from "react";

import { BrowserRouter, Route, Routes } from "react-router";
import { createRoot } from "react-dom/client";

import Gallery from "./gallery.tsx";
import "./styles.ts";
import View from "./view.tsx";

const rootElement = document.getElementById("root");

if (rootElement === null) {
  throw new Error("Need a root element!");
}

const root = createRoot(rootElement);
root.render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Gallery />} />
        <Route path="view/:imageHash" element={<View />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
);
