import { beforeEach } from "vitest";

function createMemoryStorage(): Storage {
  const values = new Map<string, string>();
  return {
    get length() {
      return values.size;
    },
    clear: () => values.clear(),
    getItem: (key) => values.get(key) ?? null,
    key: (index) => [...values.keys()][index] ?? null,
    removeItem: (key) => void values.delete(key),
    setItem: (key, value) => values.set(key, String(value)),
  };
}

if (typeof window.localStorage?.clear !== "function") {
  Object.defineProperty(window, "localStorage", { configurable: true, value: createMemoryStorage() });
}

beforeEach(() => {
  window.localStorage.clear();
});
