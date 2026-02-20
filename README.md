<div id="top">

<div align="center">

<img src="readmeai/assets/logos/purple.svg" width="30%" alt="Project Logo"/>

# AGENTIC-COUPON-FINDER

<em>AI hunts every discount, so you never miss savings.</em>

<img src="https://img.shields.io/github/license/omarg-dev/agentic-coupon-finder?style=flat-square&logo=opensourceinitiative&logoColor=white&color=0080ff" alt="license">
<img src="https://img.shields.io/github/last-commit/omarg-dev/agentic-coupon-finder?style=flat-square&logo=git&logoColor=white&color=0080ff" alt="last-commit">
<img src="https://img.shields.io/github/languages/top/omarg-dev/agentic-coupon-finder?style=flat-square&color=0080ff" alt="repo-top-language">
<img src="https://img.shields.io/github/languages/count/omarg-dev/agentic-coupon-finder?style=flat-square&color=0080ff" alt="repo-language-count">

<em>Built with the tools and technologies:</em>

<img src="https://img.shields.io/badge/SQLAlchemy-D71F00.svg?style=flat-square&logo=SQLAlchemy&logoColor=white" alt="SQLAlchemy">
<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat-square&logo=Python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/Playwright-2EAD33.svg?style=flat-square&logo=Playwright&logoColor=white" alt="Playwright">

</div>
<br>

> ⚠️ **DEVELOPMENT WARNING:** This project is in early, active development. The agentic workflows are **not yet ready for production use**. Use at your own risk.

---

<details>
  <summary>Table of Contents</summary>

- [◈ Overview](#-overview)
- [⟢ Features](#-features)
- [◇ Project Structure](#-project-structure)
  - [◊ Project Index](#-project-index)
- [⟠ Getting Started](#-getting-started)
  - [⟁ Prerequisites](#-prerequisites)
  - [⟒ Installation](#-installation)
  - [⚙ Configuration](#-configuration)
  - [⟓ Usage](#-usage)
- [⟲ Roadmap](#-roadmap)
- [⏣ Contributing](#-contributing)
- [⟶ License](#-license)

</details>

---

## ◈ Overview

**agentic-coupon-finder** is an automation pipeline that discovers, extracts, and validates e-commerce coupon codes using headless browsing with LAMs (Large Action Models).

The pipeline has three stages:

- **Discovery:** `CouponFinder` issues a DuckDuckGo search for a target domain and sends the raw result snippets to a configurable LLM for structured JSON extraction of coupon codes and descriptions.
- **Validation:** `CouponValidator` loads unverified codes from the database and dispatches a `browser-use` agent to navigate the live site, add an item to the cart, locate the promo code input, apply each code, and record whether it produced a discount.
- **Persistence:** Discovered codes, validation outcomes, and agent run logs are stored in a local SQLite database managed by SQLAlchemy, with composite unique constraints preventing duplicate entries.

---

## ⟢ Features

| Component | Details |
| :--- | :--- |
| 🔍 **Web Discovery** | `CouponFinder` queries DuckDuckGo with region-agnostic search (`wt-wt`) and filters noisy results before forwarding snippets to the LLM. |
| 🤖 **LLM Extraction** | The LLM returns a strict JSON payload `{"codes": [], "descriptions": []}`, filtered of generic words and normalized to uppercase. The provider is swappable via LangChain; Groq and Google Gemini are both supported out of the box. |
| 🧭 **Agentic Validation** | A `browser-use` `Agent` navigates real checkout flows with a 20-step safety cap, handling cart addition, promo field detection, code application, and outcome observation. |
| 🗄️ **Structured Storage** | Three SQLAlchemy models: `Website`, `Coupon`, and `TestLog`. `Coupon` enforces a `(website_id, code)` unique constraint. `TestLog` records agent run outcomes with a truncated message field. |
| 🧩 **Modular Architecture** | Discovery (`src/finder`), validation (`src/validator`), data (`src/data`), and API (`src/api`) are fully decoupled, making each layer independently replaceable. |

---

## ◇ Project Structure

```
agentic-coupon-finder/
├── main.py
├── requirements.txt
├── src/
│   ├── api/
│   │   ├── agent.py
│   │   └── server.py
│   ├── data/
│   │   ├── database.py
│   │   └── models.py
│   ├── finder/
│   │   └── collector.py
│   └── validator/
│       └── agent.py
├── storage/
│   └── coupons.db
└── testing/
    ├── init_db.py
    ├── scraping_test.py
    └── validator_test.py
```

### ◊ Project Index

<details open>
<summary><b>Root</b></summary>

| File | Summary |
| :--- | :--- |
| [requirements.txt](requirements.txt) | Python dependencies: `sqlalchemy`, `ddgs`, `browser-use`, `playwright`, `langchain-groq`, `langchain-google-genai`, `google-genai`, and `python-dotenv`. |
| [main.py](main.py) | Top-level entry point. Not yet implemented. Use the scripts in `testing/` to run individual modules directly. |

</details>

<details open>
<summary><b>src/data</b></summary>

| File | Summary |
| :--- | :--- |
| [database.py](src/data/database.py) | Configures the SQLAlchemy engine against a SQLite file at `storage/coupons.db` (overridable via `DATABASE_URL`). Exports `SessionLocal`, `Base`, and a `get_db()` generator dependency. |
| [models.py](src/data/models.py) | Three ORM models: `Website` (domain registry with audit timestamps), `Coupon` (extracted codes with `is_working` status and a `(website_id, code)` unique constraint), and `TestLog` (agent run audit trail with optional screenshot path). |

</details>

<details open>
<summary><b>src/finder</b></summary>

| File | Summary |
| :--- | :--- |
| [collector.py](src/finder/collector.py) | Implements `CouponFinder`. Executes a region-agnostic DuckDuckGo text search, forwards result snippets to the configured LLM for structured code extraction, and upserts results into the `Website` and `Coupon` tables. |

</details>

<details open>
<summary><b>src/validator</b></summary>

| File | Summary |
| :--- | :--- |
| [agent.py](src/validator/agent.py) | Implements `CouponValidator`. Runs a headless Playwright agent through a live checkout flow to test each stored code and writes a `TestLog` entry. Exposes `run_validator(domain)` as a synchronous entry point. |

</details>

<details open>
<summary><b>src/api</b></summary>

| File | Summary |
| :--- | :--- |
| [server.py](src/api/server.py) | Reserved for the HTTP API server (FastAPI). Not yet implemented. |
| [agent.py](src/api/agent.py) | Reserved for API-layer orchestration logic. Not yet implemented. |

</details>

---

## ⟠ Getting Started

### ⟁ Prerequisites

- Python 3.10+
- An API key for your chosen LLM provider (Groq and Google Gemini are both supported)

### ⟒ Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/omarg-dev/agentic-coupon-finder
    cd agentic-coupon-finder
    ```

2. Create and activate a virtual environment:

    ```sh
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # macOS / Linux
    source .venv/bin/activate
    ```

3. Install Python dependencies:

    ```sh
    pip install -r requirements.txt
    ```

4. Install the Playwright browser runtime:

    ```sh
    playwright install chromium
    ```

### ⚙ Configuration

Create a `.env` file in the project root and add the key for your chosen LLM provider:

```env
# Pick one:
GROQ_API_KEY=your_api_key_here
# GEMINI_API_KEY=your_api_key_here

# Optional: override the default SQLite path
# DATABASE_URL=sqlite:///./storage/coupons.db
```

### ⟓ Usage

**1. Initialize the database** (creates all tables):

```sh
python testing/init_db.py
```

**2. Run the discovery pipeline** against a target domain:

```sh
python testing/scraping_test.py
```

Edit `testing/scraping_test.py` to change the domain passed to `finder.find_codes()`.

**3. Run the validation agent** against codes already stored in the database:

```sh
python testing/validator_test.py
```

The script prompts for a domain name, then opens a Chromium window and runs the browser agent. Do not interact with the window during execution.

---

## ⟲ Roadmap

- [x] **Discovery pipeline**: DuckDuckGo search + LLM extraction + SQLite persistence (`CouponFinder`)
- [x] **Validation engine**: `browser-use` agent with Playwright navigates live checkout flows (`CouponValidator`)
- [x] **Database schema**: `Website`, `Coupon`, `TestLog` models with audit fields and uniqueness constraints
- [ ] **API server**: FastAPI endpoints for triggering discovery/validation and querying stored coupons (`src/api/server.py`)
- [ ] **Main entry point**: Unified `main.py` orchestrator tying all modules together
- [ ] **Result parsing**: Parse `browser-use` history output to update `Coupon.is_working` in the database

---

## ⏣ Contributing

- **[Join the Discussions](https://github.com/omarg-dev/agentic-coupon-finder/discussions)**: Share insights, propose ideas, or ask questions.
- **[Report Issues](https://github.com/omarg-dev/agentic-coupon-finder/issues)**: File bugs or feature requests.
- **[Submit Pull Requests](https://github.com/omarg-dev/agentic-coupon-finder/blob/main/CONTRIBUTING.md)**: Review open PRs or submit your own.

<details closed>
<summary>Contributing Guidelines</summary>

1. Fork the repository and clone it locally.
2. Create a descriptive feature branch: `git checkout -b feature/my-change`
3. Commit with a clear message: `git commit -m 'Add: description of change'`
4. Push and open a Pull Request against `main`.

</details>

<details closed>
<summary>Contributor Graph</summary>
<br>
<p align="left">
   <a href="https://github.com/omarg-dev/agentic-coupon-finder/graphs/contributors">
      <img src="https://contrib.rocks/image?repo=omarg-dev/agentic-coupon-finder">
   </a>
</p>
</details>

---

## ⟶ License

Released under the [MIT License](https://choosealicense.com/licenses/mit/). See the `LICENSE` file for details.

<div align="right">

[![][back-to-top]](#top)

</div>

[back-to-top]: https://img.shields.io/badge/-BACK_TO_TOP-151515?style=flat-square

---
