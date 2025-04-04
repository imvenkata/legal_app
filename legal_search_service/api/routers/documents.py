import logging
import os
import shutil
from pathlib import Path
from typing import List
from fastapi import (
    APIRouter, 
    HTTPException, 
    UploadFile, 
    File, 
    BackgroundTasks
)

# Use absolute-style imports
from legal_search_service.config import settings
from legal_search_service.api.schemas import UploadResponse
# Import the ingestion pipeline function
from legal_search_service.ingestion.pipeline import run_ingestion

logger = logging.getLogger(__name__)
router = APIRouter()

# Define the target directory for uploads (using the configured DATA_PATH)
UPLOAD_DIR = Path(settings.DATA_PATH)

# Ensure upload directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def run_ingestion_background(data_path: Path):
    """Wrapper function to run ingestion in the background."""
    logger.info(f"Background task started: Running ingestion for {data_path}")
    try:
        # Ensure the path passed is the specific directory to ingest
        run_ingestion(data_path) 
        logger.info(f"Background task finished: Ingestion for {data_path} completed.")
    except Exception as e:
        logger.error(f"Background ingestion task failed for {data_path}: {e}", exc_info=True)

@router.post(
    "/documents/upload",
    response_model=UploadResponse,
    summary="Upload Documents for Ingestion",
    description=(
        "Accepts one or more document files (PDF, DOCX, TXT). "
        "Saves the files and triggers the ingestion and embedding pipeline in the background."
    )
)
async def upload_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(..., description="List of document files to upload.")
):
    """
    Endpoint to upload documents and trigger background ingestion.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files were uploaded.")

    processed_filenames = []
    logger.info(f"Received {len(files)} file(s) for upload.")

    for file in files:
        # Basic validation (can be expanded)
        if not file.filename:
            logger.warning("Received a file without a filename. Skipping.")
            continue
            
        # TODO: Add more robust validation (file size, allowed content types)
        # allowed_extensions = [".pdf", ".docx", ".txt"]
        # file_ext = Path(file.filename).suffix.lower()
        # if file_ext not in allowed_extensions:
        #     logger.warning(f"Skipping file with unsupported extension: {file.filename}")
        #     continue
        
        try:
            # Securely create the destination path
            # Note: Using file.filename directly can be a security risk in production
            # Consider sanitizing or generating safe filenames.
            destination_path = UPLOAD_DIR / Path(file.filename).name # Basic sanitization
            
            logger.info(f"Saving uploaded file: {file.filename} to {destination_path}")
            # Save the file chunk by chunk
            with open(destination_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                
            processed_filenames.append(file.filename)
            logger.info(f"Successfully saved {file.filename}")

        except Exception as e:
            logger.error(f"Failed to save uploaded file {file.filename}: {e}", exc_info=True)
            # Decide if one failure should stop the whole batch
            raise HTTPException(status_code=500, detail=f"Failed to save file: {file.filename}. Error: {e}")
        finally:
             # Ensure the file pointer is closed
            await file.close()
            
    if not processed_filenames:
        raise HTTPException(status_code=400, detail="No valid files were processed.")

    # Add the ingestion task to run in the background
    # Pass the specific directory that was just populated/updated
    background_tasks.add_task(run_ingestion_background, UPLOAD_DIR)
    logger.info(f"Added background task to ingest documents in: {UPLOAD_DIR}")

    return UploadResponse(
        message=f"Successfully received {len(processed_filenames)} file(s). Ingestion started in background.",
        filenames=processed_filenames,
        detail=f"Ingestion triggered for directory: {UPLOAD_DIR}"
    )
