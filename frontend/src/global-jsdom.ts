import jsdom from "global-jsdom";

jsdom();

globalThis.ResizeObserver = class ResizeObserver {
  observe = () => {
  };
  unobserve = () => {
  };
  disconnect = () => {
  };
};
