import "./global-jsdom.ts";

import { assertEquals } from "@std/assert";

import { cleanup, render, screen } from "@testing-library/react";
import App from "./app.tsx";

Deno.test.beforeEach(() => {
  cleanup();
});

Deno.test("foo", () => {
  assertEquals(1, 1);
});

const expected = Deno.env.get("GREETING") ?? "";

Deno.test("renders once", async () => {
  render(App());

  const result = await screen.findByRole("heading");

  const expectedText = `Hello, ${expected}!`;

  assertEquals(result.textContent, expectedText);
});

Deno.test("renders again", async () => {
  render(App());

  const result = await screen.findByRole("heading");

  const expectedText = `Hello, ${expected}!`;
  assertEquals(result.textContent, expectedText);
});
