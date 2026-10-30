"""FastAPI entrypoint for the Motorsport Pit-Stop & Tire Strategy Optimizer."""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes_calibration import router as calibration_router
from app.api.routes_health import router as health_router
from app.api.routes_optimization import router as optimization_router
from app.api.routes_races import router as races_router
from app.api.routes_results import router as results_router
from app.api.routes_simulations import router as simulations_router
from app.core.config import settings
from app.core.exceptions import MotorsportException
from app.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown lifespan handler."""
    # Ensure database schema is initialized
    init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Stochastic race simulation and strategy optimization engine under "
        "Markovian weather, tire degradation, and Safety Car neutralizations."
    ),
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Cross-origin resource sharing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(MotorsportException)
async def motorsport_exception_handler(request: Request, exc: MotorsportException) -> JSONResponse:
    """Handle domain-specific exceptions with structured JSON error responses."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error_type": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details,
        },
    )


# Register API route modules
app.include_router(health_router)
app.include_router(calibration_router)
app.include_router(races_router)
app.include_router(simulations_router)
app.include_router(optimization_router)
app.include_router(results_router)


frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if frontend_dist.exists() and (frontend_dist / "index.html").exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
else:

    @app.get("/", include_in_schema=False)
    def root_redirect() -> RedirectResponse:
        """Redirect root path to interactive Swagger API documentation."""
        return RedirectResponse(url="/docs")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
