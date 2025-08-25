from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from contextlib import asynccontextmanager
from database import engine, Base
from routers import incidents, statistics, maps

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown

app = FastAPI(
    title="WorkerBooBoo API",
    description="Workplace Safety Data Visualization API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(incidents.router, prefix="/api/incidents", tags=["incidents"])
app.include_router(statistics.router, prefix="/api/statistics", tags=["statistics"])
app.include_router(maps.router, prefix="/api/maps", tags=["maps"])

@app.get("/")
async def root():
    return {"message": "WorkerBooBoo API - Workplace Safety Data"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "WorkerBooBoo API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
