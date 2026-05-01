# Project Starva – Design RAG Helper

Project Starva is for individuals, executives, government and companies to work together and collaborate on the same platform to manage finance and build cities with AI.
Application should have landing page 



There should be three tabs - 
Floating RAG chat button and window should always be in bottom, that can expand to fit in right side of screen like copilot when clicking button
- Monitioring Real time data and alert 
- Tools
  - Financial  Strategist - finacial Modeling
  - Capital Allocator - budget planning 
  - Risk Manager 
  - city planning and expansion - capital, payback period , breakeven timeline, what to build 

- settings, personalisation and document load 



This project is a starter template for experimenting with RAG-style (Retrieval-Augmented Generation) helpers that suggest **symbols** and **design directions** from a written brief.

Currently it includes:

- A **FastAPI backend** that stores design briefs in memory and returns simple, rule-based symbol and color recommendations (as a stand‑in for a real RAG pipeline).
- A placeholder **frontend** folder for a future Next.js UI (not fully implemented yet).

You can already run the backend and call its HTTP API from tools like cURL, Postman, or your own frontend.

---

## Project Structure

- [backend](backend)
  - [pyproject.toml](backend/pyproject.toml) – Python project definition and dependencies.
  - [app/main.py](backend/app/main.py) – FastAPI app with brief storage and suggestion endpoints.
  - [app/rag_engine.py](backend/app/rag_engine.py) – Simple rule-based "RAG" suggestion engine stub.
- [frontend](frontend) – Reserved for a future Next.js/React UI (you can scaffold it later).

---

## Backend – FastAPI

### 1. Setup Python environment

From the `backend` folder, create and activate a virtual environment (example using `venv`):

````bash
cd backend
python -m venv .venv
source .venv/bin/activate  # macOS / Linux
# .venv\\Scripts\\activate  # Windows PowerShell
``

Then install dependencies defined in `pyproject.toml` using `pip`:

```bash
pip install fastapi uvicorn[standard] pydantic
````

> Note: If you prefer to install via a build tool (hatch, poetry, etc.), you can adapt these steps.

### 2. Run the FastAPI server

From the `backend` directory with your virtual environment active:

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at:

- Base URL: `http://localhost:8000`
- OpenAPI docs (Swagger): `http://localhost:8000/docs`

---

## API Overview

The backend exposes a minimal set of endpoints for working with design briefs and getting suggestions.

### Health check

- **GET** `/health`
- Response: `{ "status": "ok" }`

### Create a brief

- **POST** `/briefs`
- Body:

```json
{
  "text": "Brand for an eco-friendly fintech app helping users track carbon footprint."
}
```

- Response example:

```json
{
  "id": 1,
  "text": "Brand for an eco-friendly fintech app helping users track carbon footprint."
}
```

### List briefs

- **GET** `/briefs`
- Response: array of stored briefs:

```json
[
  { "id": 1, "text": "..." },
  { "id": 2, "text": "..." }
]
```

### Get symbol & design suggestions

- **POST** `/suggest`
- Body:

```json
{
  "briefId": 1
}
```

- Response example (from the rule-based stub):

```json
{
  "symbols": ["leaf", "tree", "water droplet", "shield", "line chart", "coin"],
  "colorPalette": [
    "#2e7d32",
    "#66bb6a",
    "#a5d6a7",
    "#1a237e",
    "#283593",
    "#3949ab"
  ],
  "notes": "Leverage organic shapes and soft gradients to convey sustainability. Use strong geometric forms to signal trust and stability."
}
```

This structure is designed so a frontend (such as a Next.js app) can:

1. Let the user type a brief.
2. Call `POST /briefs` and show the created brief.
3. Call `POST /suggest` for a chosen brief and display the returned symbols, palette, and notes for design decisions.

---

## RAG Engine Stub and How to Extend It

The current suggestion logic lives in:

- [backend/app/rag_engine.py](backend/app/rag_engine.py)

It implements a very simple `SimpleRAGEngine` class:

- Looks for keywords like `nature`, `eco`, `finance`, `bank`, `crypto`, `tech`, `saas`, `software` in the brief text.
- Based on matches, it assembles a list of suggested `symbols`, a `color_palette`, and human-readable `notes`.
- If nothing matches, it falls back to generic abstract/monogram suggestions.

This is deliberately basic so you can replace it with a true RAG pipeline. When you are ready, you might:

1. **Add embeddings & vector store**
   - Use libraries like `sentence-transformers`, `faiss`, `chromadb`, or `pgvector` to embed:
     - Historical briefs
     - Your own symbol library (with descriptions)
     - Design guideline text (brand voice, industry-specific rules)
   - Store and query similar items to your current brief.

2. **Call an LLM for synthesis**
   - Feed the retrieved snippets (symbol descriptions, brand rules) plus the current brief to an LLM.
   - Ask it to output a structured JSON with fields similar to the current `DesignSuggestion`:
     - `symbols`: array of candidate icon names / concepts.
     - `colorPalette`: array of hex colors.
     - `notes`: short explanation of why these choices fit the brief.

3. **Wire it into `SimpleRAGEngine.suggest` or a new class**
   - You can keep the same interface and change only the internal implementation so that the API responses stay stable for your frontend.

---

## Planned Next.js Frontend (Optional for Now)

The `frontend` folder is reserved for a future Next.js app. A simple design for that UI could include:

- A main page where you:
  - Enter a new design brief in a textarea and submit it.
  - See a list of previously submitted briefs.
  - Select a brief and request suggestions.
  - Display the returned symbols, color palette (e.g., as color swatches), and notes.

When you are ready, you can:

1. Initialize a Next.js app inside `frontend` (if you prefer a clean slate):

   ```bash
   cd frontend
   npx create-next-app@latest .
   ```

2. Point the frontend to your backend (e.g., `http://localhost:8000`) and call the endpoints described above.

---

## Summary

- The backend is ready for experimentation with RAG-flavored design recommendations.
- You can plug in a more advanced symbol database, embeddings, and LLM-based reasoning inside `rag_engine.py` without changing the API shape.
- When you build a Next.js frontend, it can treat this backend as a **design recommendation microservice** to help users choose symbols and visual directions from natural language briefs.
