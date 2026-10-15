import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, vi } from "vitest";
import App from "./App";

function mockFetch(routes: Record<string, unknown>) {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url: string) => {
      const body = routes[url];
      return new Response(JSON.stringify(body ?? { detail: "introuvable" }), {
        status: body === undefined ? 404 : 200,
      });
    }),
  );
}

const renderAt = (path: string) =>
  render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>,
  );

afterEach(() => vi.unstubAllGlobals());

test("la liste montre les fiches publiées", async () => {
  mockFetch({
    "/api/films": [
      { id: 1, title: "Inception", release_date: "2010-07-15", poster_url: null, vote_average: 8.4 },
    ],
  });
  renderAt("/");
  expect(await screen.findByRole("link", { name: /Inception/ })).toHaveAttribute("href", "/films/1");
});

test("une fiche affiche l'analyse et cache la fin", async () => {
  mockFetch({
    "/api/films/1": {
      id: 1,
      title: "Inception",
      original_title: "Inception",
      release_date: "2010-07-15",
      poster_url: null,
      vote_average: 8.4,
      overview: "",
      had_subtitles: true,
      analysis: {
        synopsis: "Un voleur de rêves.",
        timeline: ["Le casse", "Les limbes"],
        ending: "La toupie tourne.",
        meta_analysis: "Rêve et réalité.",
      },
    },
  });
  renderAt("/films/1");
  expect(await screen.findByText("Un voleur de rêves.")).toBeInTheDocument();
  expect(screen.getByText("Les limbes")).toBeInTheDocument();
  expect(screen.getByText("La toupie tourne.")).not.toBeVisible();
});

test("l'admin non connecté voit le formulaire de connexion", async () => {
  mockFetch({ "/api/admin/session": { authenticated: false } });
  renderAt("/admin");
  expect(await screen.findByLabelText("Mot de passe")).toBeInTheDocument();
});
