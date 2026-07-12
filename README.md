# LinkedIn Post Generator Agent

An AI agent that plans, writes, and polishes professional LinkedIn posts — built with FastAPI, Groq and a true multi-stage agentic workflow (not a single prompt call).

---

## Project Overview

Give the agent a topic, target audience, tone, length, goal, and optional keywords and it runs a 6-stage pipeline to produce a scroll-stopping LinkedIn post:

```
User Input
   ↓
Understand Intent      (understand_request)
   ↓
Create Writing Plan    (create_post_plan)
   ↓
Generate Hook           (generate_hook)
   ↓
Generate Main Content   (generate_post)
   ↓
Improve Readability     (improve_post)
   ↓
Generate Hashtags       (generate_hashtags)
   ↓
Return Final Post       (return_final_post)
```

Each stage is an isolated Python function in `app/agent.py`, chained together in `run_agent_pipeline()`, with its own dedicated prompt in `app/prompts.py`.

---

## Features

- **True agent pipeline** — 7 discrete, explainable stages rather than one giant prompt.
- **Modern responsive UI** — vanilla HTML/CSS/JS "writing desk" interface with a live LinkedIn-style post preview.
- **Robust error handling** — friendly messages for missing API keys, invalid input, timeouts, and rate limits.
- **Dockerized** — production-ready `python:3.12-slim` image, runs identically locally and on Render.
- **Render-ready** — `render.yaml` blueprint included, reads `PORT` from the environment.
- **Typed & documented** — Pydantic models, type hints, and docstrings throughout.

---

## Screenshots

> _Add screenshots of the form and generated post preview here before publishing._

`docs/screenshot-form.png` · `docs/screenshot-output.png`

---

## Folder Structure

```
linkedin-post-agent/
│
├── app/
│   ├── __init__.py
│   ├── main.py        # FastAPI app, routing, static/template mounting
│   ├── agent.py        # 7-stage agent pipeline
│   ├── prompts.py       # Prompt templates per stage
│   ├── models.py        # Pydantic request/response models
│   ├── routes.py        # /generate and /health endpoints
│   └── utils.py         # Groq client, retries, hashtag parsing
│
├── static/
│   ├── style.css
│   └── script.js
│
├── templates/
│   └── index.html
│
├── .env.example
├── requirements.txt
├── Dockerfile
├── render.yaml
├── README.md
└── .gitignore
```

---

## Installation

```bash
git clone <your-repo-url>
cd linkedin-post-agent
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Environment Variables

Copy `.env.example` to `.env` and fill in your key:

```bash
cp .env.example .env
```

| Variable        | Required | Description                                      |
|-----------------|----------|---------------------------------------------------|
| `GROQ_API_KEY`  | Yes      | Your Groq API key from console.groq.com            |
| `GROQ_MODEL`    | No       | Model name (default: `llama-3.3-70b-versatile`)    |
| `PORT`          | No       | Port to run on locally (default: `8000`)           |

## Running Locally

```bash
uvicorn app.main:app --reload
```

Visit `http://localhost:8000` in your browser.

## Docker Commands

Build the image:

```bash
docker build -t linkedin-post-agent .
```

Run the container (pass your `.env` file at runtime):

```bash
docker run -p 8000:8000 --env-file .env linkedin-post-agent
```

Visit `http://localhost:8000`.

## Deploy on Render

1. Push this repository to GitHub.
2. In Render, choose **New +** → **Blueprint**, and point it at this repo (it will detect `render.yaml`).
3. When prompted, set the `GROQ_API_KEY` environment variable (marked `sync: false` so Render will ask for it securely).
4. Deploy — Render builds the Dockerfile and reads `PORT` automatically; no hardcoded values needed.

## API Documentation

### `POST /api/generate`

**Request body:**

```json
{
  "topic": "Lessons from shipping my first AI agent",
  "audience": "Early-career software engineers",
  "tone": "Professional",
  "length": "Medium",
  "goal": "Personal Branding",
  "keywords": "FastAPI, LangGraph, AWS"
}
```

**Response:**

```json
{
  "hook": "I shipped an AI agent that talks to five tools. Here's what broke first.",
  "post": "...",
  "hashtags": ["#AIAgents", "#FastAPI", "#SoftwareEngineering"]
}
```

**Error responses:**

| Status | Meaning                              |
|--------|----------------------------------------|
| 400/422| Invalid or missing input fields        |
| 401    | Missing/invalid Groq API key           |
| 408    | The AI service timed out               |
| 429    | Rate limit or quota exceeded           |
| 502    | The AI service failed to respond       |
| 500    | Unexpected server error                |

### `GET /api/health`

Simple liveness check, returns `{"status": "ok"}`. Used as Render's health check path.

---

## Future Improvements

- Stream each pipeline stage to the frontend over Server-Sent Events for real progress (currently the UI shows an approximate animation).
- Add a "regenerate hook only" / "regenerate hashtags only" partial-refresh mode.
- Support OpenAI as an alternate model provider via a `MODEL_PROVIDER` env toggle.
- Persist generated posts per user with a lightweight database.
- Add automated tests (pytest) for each agent stage and API error path.

---

## License

MIT License. Free to use, modify, and deploy.
