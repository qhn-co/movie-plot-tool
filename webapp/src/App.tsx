import { Link, Route, Routes } from "react-router-dom";
import AdminPage from "./pages/AdminPage";
import FilmPage from "./pages/FilmPage";
import FilmsPage from "./pages/FilmsPage";

export default function App() {
  return (
    <div className="mx-auto max-w-5xl px-4 pb-16">
      <header className="flex items-center justify-between py-6">
        <Link to="/" className="text-xl font-semibold tracking-tight">
          Movie <span className="text-amber-400">Plot</span>
        </Link>
      </header>
      <Routes>
        <Route path="/" element={<FilmsPage />} />
        <Route path="/films/:id" element={<FilmPage />} />
        <Route path="/admin" element={<AdminPage />} />
        <Route path="*" element={<p className="text-zinc-400">Page introuvable.</p>} />
      </Routes>
    </div>
  );
}
