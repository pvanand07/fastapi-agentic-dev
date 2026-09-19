# SETUP.md

Steps used to create this project from scratch. Run in order.

## 1. Scaffold the base app

```bash
mkdir project-template && cd project-template
uv init --package --name project-template
```

Gives you `pyproject.toml` (hatchling build backend), `app/__init__.py`.

## 2. Install dependencies

```bash
uv add fastapi "uvicorn[standard]" sqlalchemy alembic pydantic
uv add --dev pytest httpx ruff
```

`httpx` is required for `fastapi.testclient.TestClient`, not just for making HTTP calls.

## 3. Add the DB layer

Write `app/db.py` (SQLAlchemy engine + session factory, reads `DATABASE_URL` from the environment, defaults to local sqlite) and `app/models.py` (declarative models on `Base`).

## 4. Configure Alembic

```bash
uv run alembic init alembic
```

Edit `alembic/env.py` to import `Base` and `DATABASE_URL` from `app.db`, `import *` from `app.models` so tables register on `Base.metadata` before autogenerate runs, and set `target_metadata = Base.metadata`.

## 5. Generate the first migration

```bash
uv run alembic revision --autogenerate -m "init"
```

Produces a real migration file under `alembic/versions/`. **Do not skip this and ship an empty `alembic/versions/` directory** — `alembic upgrade head` against an empty versions dir succeeds silently (there's nothing to run), so nothing catches the mistake until something actually queries a table that was never created. Confirm the file exists and run `alembic upgrade head` against a throwaway DB before moving on:

```bash
DATABASE_URL="sqlite:///./verify.db" uv run alembic upgrade head
```

## 6. Add routes and schemas

`app/schemas.py` (Pydantic request/response models), `app/routes/*.py` (`APIRouter`, `Depends(get_db)` for the session).

FastAPI's dependency-injection pattern is `Depends(...)` as an argument default — this is idiomatic, not a bug, but `ruff`'s bugbear rule `B008` (function call in a default argument) flags it anyway. Add the ignore before it ever gets tripped over in CI:

```toml
# pyproject.toml
[tool.ruff.lint]
ignore = ["B008"]
```

## 7. Wire the entry point

`app/main.py`: construct `FastAPI()`, `include_router(...)` for each router, mount `StaticFiles(directory="static", html=True)` at `/` last (so API routes registered earlier still win).

## 8. Add tests

`tests/test_*.py` using `fastapi.testclient.TestClient`. Each test that hits a DB-backed route needs the migration from step 5 already applied against whatever `DATABASE_URL` the test run uses — `TestClient` does not create tables for you.

## 9. Add project files

`docs/domain.md`, `docs/architecture.md`, `docs/adr/`, `docs/agents/issue-tracker.md`, `docs/agents/domain.md`, `AGENT.md`, `CLAUDE.md`, `README.md`, `LICENSE`, `.env.example`, `.github/workflows/ci.yml`.

CI runs, in order: `uv sync`, `alembic upgrade head`, `ruff check .`, `pytest`. All four must be green from a fresh clone with zero changes — a template that only passes after someone edits it isn't verified.

## 10. Pin dependency versions

`uv.lock` pins exact resolved versions; commit it. Don't hand-edit version specifiers in `pyproject.toml` to be looser than what you tested against.

## 11. Verify

```bash
uv sync
rm -f *.db
DATABASE_URL="sqlite:///./ci.db" uv run alembic upgrade head
uv run ruff check .
DATABASE_URL="sqlite:///./ci.db" uv run pytest
DATABASE_URL="sqlite:///./ci.db" uv run uvicorn app.main:app --port 8000 &
sleep 1
curl -X POST http://localhost:8000/api/examples/ -H "Content-Type: application/json" -d '{"name":"smoke-test"}'
curl http://localhost:8000/api/examples/
curl -o /dev/null -w "%{http_code}\n" http://localhost:8000/
```

All of the above must pass — migration, lint, tests, and an actual write/read against the running app, not just a static check. `rm -f *.db` first: a stale local `app.db`/`ci.db` from a previous run can mask a broken migration by already having the table.

## 12. Set up Matt Pocock's skills (optional, once per repo)

If this repo uses the `mattpocock/skills` set (`grill-with-docs`, `to-spec`, `to-tickets`, `implement`, `code-review`, etc. — see `AGENT.md`'s Flow section), run this once the repo has a real git remote, before using any of those skills for real.

Install the skills this project actually uses, in one command, run from the repo root. `--skill` (`-s`) takes a space-separated list — it does not accept `--skill=<name>` repeated per invocation; each of those installs the entire 38-skill package instead of just the named one, so don't split this into one command per skill. No `-g`: omitting it installs to the project (`.agents/skills/`), not globally.

```bash
npx skills@latest add mattpocock/skills --skill setup-matt-pocock-skills ask-matt grill-with-docs to-spec to-tickets implement code-review tdd codebase-design grilling domain-modeling -y
```

This writes skill content under `.agents/skills/` (symlinked into `.claude/skills/` etc. per agent) and a `skills-lock.json` manifest. `.agents/skills/` and `.claude/skills/` should be gitignored — they're fetched content, not source — but `skills-lock.json` is committed. After a fresh clone, restore them with:

```bash
npx skills experimental_install
```

`codebase-design`, `grilling`, and `domain-modeling` are not optional extras — `tdd` depends on `codebase-design` directly, and `grill-with-docs` is a one-line delegation to `grilling` + `domain-modeling`. Skipping any of the three leaves the skill that depends on it non-functional.

If you ever land with the full 38-skill set installed (e.g. from running `add` without `--skill`), prune back to just the required set:

```bash
npx skills@latest remove --all -y
npx skills@latest add mattpocock/skills --skill setup-matt-pocock-skills ask-matt grill-with-docs to-spec to-tickets implement code-review tdd codebase-design grilling domain-modeling -y
```

Add later, only if the need actually comes up (not part of this project's default flow) — same multi-name syntax:

```bash
npx skills@latest add mattpocock/skills --skill handoff   # a session runs out of context mid-task
npx skills@latest add mattpocock/skills --skill triage    # issues arrive faster than they can be scoped by hand
```

Then run the setup skill:

```
/setup-matt-pocock-skills
```

It's non-invokable — the agent never reaches for it on its own, someone has to type the command. It reads `git remote`, proposes GitHub as the issue tracker, and writes `docs/agents/issue-tracker.md` and `docs/agents/domain.md`, replacing the stubs from step 9. It also appends an `## Agent skills` block to `CLAUDE.md`.

Two things it does **not** do:

- `docs/agents/triage-labels.md` is only written if the `triage` skill is installed. This template's `AGENT.md` flow doesn't use `triage` — skip expecting this file unless `triage` gets added later.
- It maps label *names* to roles, it doesn't create them. On a fresh GitHub repo, `ready-for-agent`, `needs-info`, `ready-for-human`, `wontfix` still need to be created by hand (`gh label create ...`) the first time.

Re-run it only to switch trackers or start over — not on every session.

## 13. Clean up before committing

```bash
rm -rf .venv __pycache__ .pytest_cache .ruff_cache *.db
```

Regenerated by `uv sync` / `pytest` / `ruff` / `alembic upgrade` respectively. Don't ship them in the template.
