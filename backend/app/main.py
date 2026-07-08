from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.interactions import router as interactions_router
from app.core.config import settings

app = FastAPI(title="hcp-crm-ai", version="0.1.0")

# The React app runs on a separate dev server, so CORS must allow that origin locally.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Keep interaction routes grouped under one prefix as the module grows.
app.include_router(interactions_router, prefix="/api/interactions", tags=["interactions"])


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}

