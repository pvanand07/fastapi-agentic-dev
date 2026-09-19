from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes import example

app = FastAPI(title="project-template")

app.include_router(example.router)

app.mount("/", StaticFiles(directory="static", html=True), name="static")
