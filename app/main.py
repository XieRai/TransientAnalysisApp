"""FastAPI application entry point."""
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.routes import router

app = FastAPI(title="Transient Analyzer", version="1.0.0")
APP_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
templates = Jinja2Templates(directory=APP_DIR / "templates")
app.include_router(router)


@app.get("/", include_in_schema=False)
async def dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")
