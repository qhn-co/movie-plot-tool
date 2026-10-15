import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, type FilmCard, year } from "../api";
import Poster from "../components/Poster";

export default function FilmsPage() {
  const [films, setFilms] = useState<FilmCard[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    api.films().then(setFilms, (e: Error) => setError(e.message));
  }, []);

  if (error) return <p className="text-red-400">{error}</p>;
  if (!films) return <p className="text-zinc-400">Chargement…</p>;
  if (films.length === 0) return <p className="text-zinc-400">Aucune fiche publiée pour l'instant.</p>;

  const needle = filter.trim().toLowerCase();
  const shown = films.filter((f) => f.title.toLowerCase().includes(needle));

  return (
    <>
      <input
        type="search"
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
        placeholder="Filtrer les films"
        aria-label="Filtrer les films"
        className="mb-6 w-full rounded-lg border border-zinc-800 bg-zinc-900 px-4 py-2 outline-none focus:border-amber-400"
      />
      <ul className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
        {shown.map((film) => (
          <li key={film.id}>
            <Link to={`/films/${film.id}`} className="group block">
              <Poster url={film.poster_url} title={film.title} className="group-hover:opacity-80" />
              <p className="mt-2 font-medium">{film.title}</p>
              <p className="text-sm text-zinc-400">{year(film.release_date)}</p>
            </Link>
          </li>
        ))}
      </ul>
    </>
  );
}
