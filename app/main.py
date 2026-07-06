"""
FastAPI application entrypoint for the LinkedIn Post Generator Agent.
"""

import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routes import router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("linkedin_agent")

# Explicitly locate and load the .env file from the project root, regardless
# of the directory the app is launched from. This avoids the common issue
# where `load_dotenv()` silently fails to find the file when uvicorn is run
# from a different working directory.
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ENV_PATH = os.path.join(_PROJECT_ROOT, ".env")

if os.path.exists(_ENV_PATH):
    load_dotenv(dotenv_path=_ENV_PATH, override=True)
    logger.info("Loaded environment variables from %s", _ENV_PATH)
else:
    logger.warning(
        "No .env file found at %s. Falling back to system environment variables only.",
        _ENV_PATH,
    )

if os.getenv("GROQ_API_KEY"):
    logger.info("GROQ_API_KEY detected - Groq calls are enabled.")
else:
    logger.warning(
        "GROQ_API_KEY is NOT set. /api/generate will return 401 until it is configured."
    )

app = FastAPI(
    title="LinkedIn Post Generator Agent",
    description="A multi-stage AI agent that plans, writes, and polishes LinkedIn posts.",
    version="1.0.0",
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app.include_router(router, prefix="/api")


@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request) -> HTMLResponse:
    """Serve the main single-page frontend."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Return a clean, user-friendly error message for invalid/empty input
    instead of a raw FastAPI traceback-style validation error.
    """
    errors = exc.errors()
    messages = []
    for err in errors:
        field = ".".join(str(loc) for loc in err.get("loc", []) if loc != "body")
        messages.append(f"{field}: {err.get('msg')}")

    logger.warning("Request validation failed: %s", messages)
    return JSONResponse(
        status_code=422,
        content={"error": "Invalid input provided.", "detail": messages},
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
