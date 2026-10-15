import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, type FilmPage as FilmData, year } from "../api";
import Analysis from "../components/Analysis";
import Poster from "../components/Poster";

export default function FilmPage() {
  const { id } = useParams();
  const [film, setFilm] = useState<FilmData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.film(Number(id)).then(setFilm, (e: Error) => setError(e.message));
  }, [id]);

  if (error) return <p className="text-red-400">{error}</p>;
  if (!film) return <p className="text-zinc-400">Chargement…</p>;

  return (
    <article className="grid gap-8 md:grid-cols-[220px_1fr]">
      <div>
        <Poster url={film.poster_url} title={film.title} />
        <Link to="/" className="mt-4 inline-block text-sm text-zinc-400 hover:text-zinc-200">
          ← Tous les films
        </Link>
      </div>
      <div>
        <h1 className="text-3xl font-semibold">{film.title}</h1>
        <p className="mb-8 mt-1 text-zinc-400">
          {year(film.release_date)}
          {film.original_title !== film.title && ` · ${film.original_title}`}
          {film.vote_average > 0 && ` · ${film.vote_average.toFixed(1)}/10 sur TMDB`}
        </p>
        <Analysis analysis={film.analysis} />
      </div>
    </article>
  );
}
