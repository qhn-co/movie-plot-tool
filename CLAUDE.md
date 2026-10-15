# CLAUDE.md — Movie Plot

Movie Plot (`movieplot.qhn.fr`) publie des fiches de films qui aident à se rappeler un film et à savoir si on l'a vu : accroche, scènes marquantes, synopsis, chronologie, fin masquée, contexte. Le prompt est dans `src/movieplot/summarizer.py` ; on le valide sur des exemples avant de le changer. Un admin cherche un film sur TMDB, fait générer la fiche par Claude à partir des sous-titres OpenSubtitles, la relit et la publie ; le public ne fait que lire. Python 3.12 + FastAPI, PostgreSQL (SQLite en local par défaut), front React/Vite/TypeScript servi par l'API, un seul conteneur. Hébergé sur le Coolify de Steven. Projet personnel : process proportionné.

## Commandes

```
make install   # dépendances Python (uv) et front (npm ci)
make check     # lint + typecheck + tests, Python et front : le gate de toute PR
make run       # API sur :8000 (lit .env s'il existe)
make web       # front sur :3000, relaie /api vers :8000
make db-up     # PostgreSQL local (compose.yaml)
make image     # image Docker locale
```

## Écrire le code

- Vocabulaire anglais dans le code et l'API ; l'interface et les messages d'erreur visibles restent en français.
- Une docstring dit ce que fait le code et pourquoi, au présent, en quelques lignes. L'historique va dans la PR et le commit.
- Les services externes (TMDB, OpenSubtitles, Claude) sont derrière une interface ; les tests utilisent des faux et ne touchent jamais le réseau.
- Un test qui revendique une garde doit rougir quand on casse la garde : le vérifier une fois à la main.
- Une révision Alembic par PR au plus, dans `src/movieplot/db/migrations/versions/` ; `tests/test_migrations.py` vérifie qu'elle colle aux modèles.

## Données et secrets

- Le dépôt est public : aucun secret, aucune base, aucun `.env` commité. Les clés vivent dans les variables d'environnement de l'application Coolify.
- Déployé (`MOVIEPLOT_ENV` renseigné), l'application refuse de démarrer sans `ADMIN_PASSWORD`, `SESSION_SECRET` de 32 caractères et une base PostgreSQL.
- Un credential vu en clair est à tourner.

## Livrer

- Une branche et une PR par mission, ≤ ~1 000 lignes ajoutées hors fichiers générés (un dépassement se dit dans la PR).
- Merge en squash quand `make check` est vert en CI sur une tête à jour avec `master`.
- La CI publie l'image `ghcr.io/qhn-co/movie-plot-tool:<sha>` à chaque push sur `master`. Rien ne part en production sans l'accord explicite de Steven.
- Commits : `<type>(<scope>): <description en français>`.
