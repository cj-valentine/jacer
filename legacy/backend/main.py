from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import tasks, today, schedule, templates, history

app = FastAPI(title="Jacer API")

# Configure CORS for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(today.router, prefix="/api/today", tags=["Today"])
app.include_router(schedule.router, prefix="/api/schedule", tags=["Schedule"])
app.include_router(templates.router, prefix="/api/templates", tags=["Templates"])
app.include_router(history.router, prefix="/api/history", tags=["History"])

@app.get("/")
def read_root():
    return {"message": "Jacer API is running"}
