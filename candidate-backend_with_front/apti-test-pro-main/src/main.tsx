console.log("=== main.tsx: START ===");

import "./index.css";

console.log("CSS loaded");

import { createRoot } from "react-dom/client";
console.log("createRoot imported");

import { ErrorBoundary } from "./components/ErrorBoundary";
console.log("ErrorBoundary imported");

import App from "./App.tsx";
console.log("App imported");

const rootElement = document.getElementById("root");
console.log("Root element found:", !!rootElement);

if (!rootElement) {
  const msg = "ROOT ELEMENT NOT FOUND!";
  console.error(msg);
  document.body.innerHTML = `<div style="color:red;padding:20px;font-family:monospace"><h1>${msg}</h1></div>`;
  throw new Error(msg);
}

console.log("Creating React root...");
const root = createRoot(rootElement);
console.log("Root created, rendering...");

root.render(
  <ErrorBoundary>
    <App />
  </ErrorBoundary>
);

window.__APP_LOADED__ = true;
console.log("=== main.tsx: SUCCESS ===");




