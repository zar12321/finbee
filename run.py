# run.py

import uvicorn

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from starlette.middleware.sessions import (
    SessionMiddleware
)

# =====================================================
# ROUTERS
# =====================================================

from app.routers.auth import (
    router as auth_router
)

from app.routers.dashboard import (
    router as dashboard_router
)

from app.routers.transaction import (
    router as transaction_router
)

from app.routers.profile import (
    router as profile_router
)

from app.routers.analysis import (
    router as analysis_router
)

# =====================================================
# APP
# =====================================================

app = FastAPI(
    title="FinBee",
    version="1.0.0"
)

# =====================================================
# SESSION
# =====================================================

app.add_middleware(
    SessionMiddleware,
    secret_key="finbee-secret-key"
)

# =====================================================
# STATIC
# =====================================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

# =====================================================
# ROUTERS
# =====================================================

app.include_router(auth_router)

app.include_router(dashboard_router)

app.include_router(transaction_router)

app.include_router(profile_router)

app.include_router(analysis_router)

# =====================================================
# HOME
# =====================================================

@app.get("/")
def home():

    return RedirectResponse(
        url="/auth/login"
    )

# =====================================================
# HEALTH
# =====================================================

@app.get("/health")
def health():

    return {
        "status": "ok"
    }

# =====================================================
# RUN
# =====================================================

if __name__ == "__main__":

    uvicorn.run(
        "run:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )