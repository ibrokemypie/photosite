import React from "npm:react";
import { createRoot } from "npm:react-dom/client";

import App from "./app.tsx";

const rootElement = document.getElementById("root");

if (rootElement === null) {
  throw new Error("Need a root element!");
}

const root = createRoot(rootElement);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
