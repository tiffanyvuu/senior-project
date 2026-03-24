from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routes.students import router as students_router

app = FastAPI(title="Pedagogical AI Agent API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(students_router)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
