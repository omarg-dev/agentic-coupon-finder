# Coupon Scraper with LAM - Copilot Instructions

## 🏗 Project Overview
This is a modular system for scraping, storing, and validating discount codes using a planned Large Action Model (LAM).

### Core Architecture
- **Data Layer** (`src/data/`): SQLAlchemy + SQLite (`./storage/coupons.db`).
- **Finder** (`src/finder/`): Coupon data collection (currently using DuckDuckGo).
- **Validator** (`src/validator/`): *[In Progress]* Logic to validate codes via browser automation/LAM.
- **API** (`src/api/`): *[In Progress]* Interface for external access.

## 🚀 Developer Workflow

### Database Management
- **Type**: SQLite
- **Models**: Defined in `src/data/models.py`.
- **Initialization**: Run `python testing/init_db.py` to create tables.
- **Session**: Use `src.data.database.SessionLocal` for DB interactions.

### Running Components
- **Scraper**: Trigger the finding logic via `src/finder/collector.py`.
- **Project Root**: Execute commands from the root directory to ensure `src` imports resolve correctly.

## 📝 Conventions & Patterns

### Database (SQLAlchemy)
- **Relationships**: Explicitly define `back_populates` and `cascade="all, delete-orphan"` where appropriate.
- **Uniqueness**: Use `UniqueConstraint` in `__table_args__` for composite keys (e.g., website + code).
- **Session Handling**: Always commit changes and close sessions (or use context managers/dependencies).

### Python
- **Pathing**: Prefer running modules via `python -m src...` to avoid `sys.path` hacks.
- **Scraping**: Handle rate limits (sleeps) and user-agents politely when using `duckduckgo_search`.

### Missing/Pending
- `main.py` is currently empty; needs an entry point orchestrator.
- `src/api` and `src/validator` structures exist but files are empty.
