# Movie Plot

Des fiches de films en lecture libre : synopsis, chronologie, fin (masquée par défaut) et analyse. Les fiches sont générées par un admin, relues, puis publiées.

## Comment ça marche

1. Dans `/admin`, l'admin cherche un film sur TMDB et clique sur « Générer ».
2. L'API récupère la fiche TMDB, les sous-titres OpenSubtitles (par identifiant IMDb) et demande à Claude une analyse structurée à partir des sous-titres complets.
3. La fiche est enregistrée en brouillon ; l'admin la publie, la dépublie, la régénère ou la supprime.
4. Le public parcourt les fiches publiées sur `/` et les lit sur `/films/<id>`.

Sans sous-titres (OpenSubtitles en panne ou film absent), la fiche est générée à partir du résumé TMDB et marquée « sans sous-titres » côté admin.

## Démarrer en local

```bash
cp .env.example .env   # renseigner les clés et ADMIN_PASSWORD
make install
make run               # API sur http://localhost:8000
make web               # front sur http://localhost:3000
```

Pour générer une fiche sans l'enregistrer : `uv run --env-file .env movieplot preview "Inception"`.

## Déploiement (Coolify)

L'image `ghcr.io/qhn-co/movie-plot-tool:<sha>` est publiée par la CI à chaque push sur `master`. Dans Coolify : une application à partir de cette image (port 8000), une base PostgreSQL, et les variables de `.env.example` avec `MOVIEPLOT_ENV=production`. Le conteneur applique les migrations au démarrage et expose `/api/health` et `/api/version`.
