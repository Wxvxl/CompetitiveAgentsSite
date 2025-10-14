# Competitive Agents Site

Full-stack platform for the CITS3011/5206 “Competitive Agents” assignments.  
Students upload Python agents, administrators configure contests, and tournament results are tracked in one dashboard.

## Repository Layout
```
CompetitiveAgentsSite/
├─ competitive-agent-site/   # Next.js 15 frontend
└─ PythonWebserver/          # Flask API, Docker, PostgreSQL schema
```

## Prerequisites
- Node.js 20+ and npm 10+
- Docker Engine + Docker Compose
- (Optional) Python 3.11+ for running backend utilities outside Docker

## Quick Start
1. Clone and install dependencies
   ```bash
   git clone <repo-url>
   cd CompetitiveAgentsSite
   npm install --prefix competitive-agent-site
   ```
2. Configure backend environment variables  
   Create `PythonWebserver/.env` with values that match Docker/PostgreSQL setup (the defaults below align with `docker-compose.yml` and `dbSetup.py`):
   ```env
   POSTGRES_DB=test
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=admin
   SECRET_KEY=project-challenge-secret
   DATABASE_URL=postgresql://postgres:admin@db:5432/test

   ```
3. Start backend services (this runs `dbSetup.py` and `appTesting.py` before starting Flask, so the database is recreated on each launch)
   ```bash
   cd PythonWebserver
   docker compose up --build
   ```
4. Launch the frontend
   ```bash
   cd ../competitive-agent-site
   npm run dev
   ```
5. Open http://localhost:3000 (API defaults to http://localhost:5001).  
   Override the API origin by creating `competitive-agent-site/.env.local`:
   ```env
   NEXT_PUBLIC_API_BASE=http://localhost:5001
   ```

## Working with the Frontend (`competitive-agent-site/`)
- `npm run dev` – start the Next.js dev server with hot reload on `app/page.tsx` and other routes
- `npm run build` – produce an optimized production build
- `npm run start` – serve the production build
- `npm run lint` – run ESLint using the project configuration

## Working with the Backend (`PythonWebserver/`)
- `docker compose up --build` – build and start the Flask API + PostgreSQL stack (runs `dbSetup.py` + `appTesting.py` automatically)
- `docker compose exec app python dbSetup.py` – manually recreate tables (destructive; use to reset the environment)
- `docker compose exec app python appTesting.py` – re-run API smoke tests after manual changes
- Games must live under `PythonWebserver/games/` and expose a `Game` class with `play()` returning the match result; see inline comments and existing games for guidance.

## Further Reading
- `ARCHITECTURE_CONTESTS.md`
- `API_CONTEST_REFERENCE.md`
- `CONTEST_IMPLEMENTATION.md`
- `TESTING_CONTESTS.md`
- `FILES_CHANGED_CONTESTS.md`
