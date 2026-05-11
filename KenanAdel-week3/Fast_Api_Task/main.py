from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from routers import users, projects, tasks
from database import Base, engine

import models.user, models.project, models.task
from fastapi.middleware.cors import CORSMiddleware
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI SQLAlchemy CRUD Example")

app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ CORS Configuration

origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # أو ["*"] للتجربة فقط
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)

@app.get("/")
def serve_frontend():
    return FileResponse(os.path.join(os.path.dirname(__file__), "index.html"))
