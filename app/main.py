from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from core.constants import APP_NAME
from core.constants import APP_VERSION


# =====================================================
# FASTAPI APP
# =====================================================

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)


# =====================================================
# STATIC FILES
# =====================================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# =====================================================
# TEMPLATES
# =====================================================

templates = Jinja2Templates(
    directory="app/templates"
)


# =====================================================
# ROOT ENDPOINT
# =====================================================

@app.get("/")
def root():
    return {
        "application": APP_NAME,
        "version": APP_VERSION,
        "status": "running"
    }


# =====================================================
# HEALTH CHECK
# =====================================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }