import { type FormEvent, useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { type AdminFilm, api, type TmdbResult, year } from "../api";

const button =
  "rounded-md px-3 py-1.5 text-sm font-medium disabled:opacity-50 bg-zinc-800 hover:bg-zinc-700";
const primary =
  "rounded-md px-3 py-1.5 text-sm font-medium disabled:opacity-50 bg-amber-400 text-zinc-950 hover:bg-amber-300";

export default function AdminPage() {
  const [authenticated, setAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    api.session().then((s) => setAuthenticated(s.authenticated), () => setAuthenticated(false));
  }, []);

  if (authenticated === null) return <p className="text-zinc-400">Chargement…</p>;
  if (!authenticated) return <Login onLogin={() => setAuthenticated(true)} />;
  return <Dashboard onLogout={() => setAuthenticated(false)} />;
}

function Login({ onLogin }: { onLogin: () => void }) {
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    try {
      await api.login(password);
      onLogin();
    } catch (e) {
      setError((e as Error).message);
    }
  };

  return (
    <form onSubmit={submit} className="mx-auto mt-16 max-w-sm space-y-4">
      <h1 className="text-2xl font-semibold">Espace admin</h1>
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        aria-label="Mot de passe"
        placeholder="Mot de passe"
        autoComplete="current-password"
        className="w-full rounded-lg border border-zinc-800 bg-zinc-900 px-4 py-2 outline-none focus:border-amber-400"
      />
      {error && <p className="text-sm text-red-400">{error}</p>}
      <button type="submit" className={primary}>
        Se connecter
      </button>
    </form>
  );
}

function Dashboard({ onLogout }: { onLogout: () => void }) {
  const [films, setFilms] = useState<AdminFilm[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<number | null>(null);

  const refresh = useCallback(() => {
    api.adminFilms().then(setFilms, (e: Error) => setError(e.message));
  }, []);
  useEffect(refresh, [refresh]);

  const run = async (key: number, action: () => Promise<unknown>) => {
    setBusy(key);
    setError(null);
    try {
      await action();
      refresh();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(null);
    }
  };

  const logout = async () => {
    await api.logout();
    onLogout();
  };

  return (
    <div className="space-y-10">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Fiches</h1>
        <button type="button" onClick={logout} className={button}>
          Se déconnecter
        </button>
      </div>
      {error && <p className="text-red-400">{error}</p>}
      <TmdbSearch
        busy={busy}
        onGenerate={(r) => run(r.tmdb_id, () => api.generate(r.tmdb_id))}
        existing={new Set(films.map((f) => f.tmdb_id))}
      />
      <table className="w-full text-left text-sm">
        <thead className="text-zinc-400">
          <tr>
            <th className="py-2">Film</th>
            <th>État</th>
            <th className="text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          {films.map((film) => (
            <tr key={film.id} className="border-t border-zinc-800">
              <td className="py-3">
                {film.title} <span className="text-zinc-500">{year(film.release_date)}</span>
                {!film.had_subtitles && (
                  <span className="ml-2 text-xs text-amber-500">sans sous-titres</span>
                )}
              </td>
              <td>{film.published ? "Publiée" : "Brouillon"}</td>
              <td className="space-x-2 py-3 text-right">
                {film.published && (
                  <Link to={`/films/${film.id}`} className={button}>
                    Voir
                  </Link>
                )}
                <button
                  type="button"
                  className={button}
                  disabled={busy !== null}
                  onClick={() => run(film.tmdb_id, () => api.setPublished(film.id, !film.published))}
                >
                  {film.published ? "Dépublier" : "Publier"}
                </button>
                <button
                  type="button"
                  className={button}
                  disabled={busy !== null}
                  onClick={() => run(film.tmdb_id, () => api.generate(film.tmdb_id))}
                >
                  {busy === film.tmdb_id ? "…" : "Régénérer"}
                </button>
                <DeleteButton disabled={busy !== null} onConfirm={() => run(film.tmdb_id, () => api.remove(film.id))} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function DeleteButton({ onConfirm, disabled }: { onConfirm: () => void; disabled: boolean }) {
  const [armed, setArmed] = useState(false);
  return (
    <button
      type="button"
      disabled={disabled}
      className={`${button} ${armed ? "bg-red-700 hover:bg-red-600" : ""}`}
      onClick={() => (armed ? onConfirm() : setArmed(true))}
      onBlur={() => setArmed(false)}
    >
      {armed ? "Confirmer" : "Supprimer"}
    </button>
  );
}

type SearchProps = {
  busy: number | null;
  existing: Set<number>;
  onGenerate: (result: TmdbResult) => void;
};

function TmdbSearch({ busy, existing, onGenerate }: SearchProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<TmdbResult[]>([]);

  useEffect(() => {
    if (query.trim().length < 2) return;
    const timer = setTimeout(() => {
      api.searchTmdb(query).then(setResults, () => setResults([]));
    }, 300);
    return () => clearTimeout(timer);
  }, [query]);

  return (
    <section>
      <input
        type="search"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Chercher un film sur TMDB"
        aria-label="Chercher un film sur TMDB"
        className="w-full rounded-lg border border-zinc-800 bg-zinc-900 px-4 py-2 outline-none focus:border-amber-400"
      />
      <ul className="mt-2 divide-y divide-zinc-800">
        {(query.trim().length < 2 ? [] : results).map((r) => (
          <li key={r.tmdb_id} className="flex items-center justify-between py-2">
            <span>
              {r.title} <span className="text-zinc-500">{r.year}</span>
            </span>
            <button
              type="button"
              className={primary}
              disabled={busy !== null || existing.has(r.tmdb_id)}
              onClick={() => onGenerate(r)}
            >
              {busy === r.tmdb_id ? "Génération…" : existing.has(r.tmdb_id) ? "Déjà créée" : "Générer"}
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
