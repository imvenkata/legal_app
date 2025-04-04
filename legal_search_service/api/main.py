from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .routers import search
from .routers import documents
from legal_search_service.config import settings

# Define allowed origins (update if your frontend runs on a different port)
origins = [
    "http://localhost:3000",
    "http://localhost:3001", # Add other potential frontend ports if needed
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    # Add deployed frontend URL here later
]

app = FastAPI(
    title="Legal Search Service API",
    description="API for ingesting documents and performing legal search.",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods
    allow_headers=["*"], # Allow all headers
)

# Mount the data directory for serving original documents
data_directory = Path(settings.DATA_PATH)
static_files_path = Path(__file__).parent.parent / data_directory # Assumes main.py is in api/ and data is relative to project root
# Ensure the path exists before mounting
if static_files_path.is_dir():
    app.mount("/api/v1/documents", StaticFiles(directory=static_files_path), name="documents_static")
    print(f"Serving static files from: {static_files_path}") # Log path for debugging
else:
    print(f"Warning: Static files directory not found: {static_files_path}. Document links may not work.")

@app.get("/", tags=["Health"])
def read_root():
    """Root endpoint for health check."""
    return {"status": "ok", "message": "Welcome to the Legal Search Service API"}

# Add routers
app.include_router(search.router, prefix="/api/v1", tags=["Search & RAG"])
app.include_router(documents.router, prefix="/api/v1", tags=["Documents"])
