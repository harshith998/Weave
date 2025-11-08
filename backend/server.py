"""
Minimal FastAPI server for Emergent preview compatibility.
This is a placeholder to allow the preview URL routing to work.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Weave Backend (Minimal)")

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "ok", "message": "Weave backend placeholder"}

@app.get("/api/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/status")
async def status():
    return {"status": "ready", "frontend": "operational"}
