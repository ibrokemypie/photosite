import "./global-jsdom.ts";

import { afterEach, describe, it } from "jsr:@std/testing/bdd";
import { assertEquals } from "jsr:@std/assert";

import { cleanup, render, screen } from "npm:@testing-library/react";
import App from "./app.tsx";

describe("App component", () => {
  afterEach(() => {
    cleanup();
  });

  it("renders once", async () => {
    render(App());

    const result = await screen.findByRole("heading");

    const expectedText = "Hello, blah!";
    assertEquals(result.textContent, expectedText);
  });

  it("renders again", async () => {
    render(App());

    const result = await screen.findByRole("heading");

    const expectedText = "Hello, blah!";
    assertEquals(result.textContent, expectedText);
  });
});
