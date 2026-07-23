# UniSco

Unisco — Personalized scholarship &amp; grant matching for Daejeon university students.

See [PROJECT_BRIEF.md](./PROJECT_BRIEF.md) for background, scope, and rationale.

## Stack

- **Backend**: FastAPI (Python 3.13) + SQLModel
- **Frontend**: Next.js (App Router) + React + TypeScript + Tailwind CSS
- **Database**: PostgreSQL (Supabase — hosted, includes a spreadsheet-like Studio UI for non-technical data entry)

## Project layout

```
UniSco/
├── backend/            # FastAPI app
│   ├── app/
│   │   ├── api/        # route modules
│   │   ├── core/       # config/settings
│   │   ├── db/         # DB session/engine
│   │   ├── models/     # SQLModel table models (empty — feature work starts here)
│   │   └── main.py     # app entrypoint
│   ├── venv/           # local virtualenv (gitignored)
│   ├── requirements.txt
│   └── .env.example
└── frontend/            # Next.js app (standard create-next-app layout)
    └── .env.example
```

## Local setup

### Backend

```bash
cd backend
python3.13 -m venv venv        # already created; recreate if missing
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env           # fill in real DATABASE_URL once Supabase project exists
uvicorn app.main:app --reload  # http://localhost:8000
```

Check it's alive: `curl http://localhost:8000/health` → `{"status": "ok"}`

Lint: `ruff check .` (run from `backend/`, with venv active)

### Frontend

```bash
cd frontend
npm install                    # already run once during scaffolding
cp .env.example .env.local
npm run dev                    # http://localhost:3000
```

## Next steps (feature work starts here)

Nothing below this line is implemented yet — this session only set up the skeleton.

1. **Provision Supabase project** — create it, get the Postgres connection string into `backend/.env`, and give the friend doing data collection access to Supabase Studio.
2. **Define the data model** (`backend/app/models/`): `Scholarship`, eligibility rule fields (school year, major, income bracket, region, military status, etc.), and how a user "spec" maps to eligibility. This is the schema the friend's manually-collected data needs to fit.
3. **Seed initial scholarship data** — manual/semi-manual entry via Supabase Studio per the brief's "not full automated scraping yet" scope.
4. **Matching endpoint** — `POST /match` (or similar) in `backend/app/api/`: takes a user spec, filters scholarships by eligibility rules, returns matches. Rule-based only for v1, no ML.
5. **Frontend spec-input form + results list** — the one-time input → personalized list flow described as the MVP's core differentiator.
6. **Migrations** — pick a migration tool once the schema stabilizes (Alembic works with SQLModel).
