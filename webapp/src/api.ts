// Client de l'API : les types reprennent les schémas de `movieplot.api.schemas`.

export type Analysis = {
  synopsis: string;
  timeline: string[];
  ending: string;
  meta_analysis: string;
};

export type FilmCard = {
  id: number;
  title: string;
  release_date: string;
  poster_url: string | null;
  vote_average: number;
};

export type FilmPage = FilmCard & {
  original_title: string;
  overview: string;
  analysis: Analysis;
  had_subtitles: boolean;
};

export type AdminFilm = FilmPage & {
  tmdb_id: number;
  published: boolean;
  model: string;
  updated_at: string;
};

export type TmdbResult = { tmdb_id: number; title: string; year: string };

export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: init?.body ? { "Content-Type": "application/json" } : undefined,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new ApiError(response.status, body?.detail ?? `Erreur ${response.status}`);
  }
  return response.status === 204 ? (undefined as T) : response.json();
}

const json = (method: string, body: unknown): RequestInit => ({
  method,
  body: JSON.stringify(body),
});

export const api = {
  films: () => request<FilmCard[]>("/api/films"),
  film: (id: number) => request<FilmPage>(`/api/films/${id}`),
  session: () => request<{ authenticated: boolean }>("/api/admin/session"),
  login: (password: string) => request("/api/admin/session", json("POST", { password })),
  logout: () => request("/api/admin/session", { method: "DELETE" }),
  adminFilms: () => request<AdminFilm[]>("/api/admin/films"),
  searchTmdb: (q: string) =>
    request<TmdbResult[]>(`/api/admin/tmdb/search?q=${encodeURIComponent(q)}`),
  generate: (tmdbId: number) =>
    request<AdminFilm>("/api/admin/films", json("POST", { tmdb_id: tmdbId })),
  setPublished: (id: number, published: boolean) =>
    request<AdminFilm>(`/api/admin/films/${id}`, json("PATCH", { published })),
  remove: (id: number) => request(`/api/admin/films/${id}`, { method: "DELETE" }),
};

export const year = (date: string) => date.slice(0, 4);
