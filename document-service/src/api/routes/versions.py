from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Path
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

from src.db.session import get_db
from src.db.models import DocumentVersion, DocumentVersionCreate, DocumentVersionResponse
from src.core.storage import get_storage_service
from src.core.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=DocumentVersionResponse, status_code=status.HTTP_201_CREATED)
async def create_document_version(
    document_id: str = Path(...),
    file: UploadFile = File(...),
    comment: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Upload a new version of an existing document.
    """
    # This would be replaced with actual database call
    # document = get_document_by_id(db, document_id)
    # if document.owner_id != current_user["id"]:
    #     raise HTTPException(status_code=403, detail="Not authorized to update this document")
    
    # Generate unique ID for version
    version_id = str(uuid.uuid4())
    
    # Get file info
    file_size = 0
    file_content = await file.read()
    file_size = len(file_content)
    
    # Get file extension
    if "." in file.filename:
        file_extension = file.filename.split(".")[-1]
    else:
        file_extension = ""
    
    # Get storage service
    storage = get_storage_service()
    
    # Store file
    storage_path = f"{document_id}/versions/{version_id}.{file_extension}"
    await storage.store_file(storage_path, file_content)
    
    # Create version in database
    version = DocumentVersionCreate(
        document_id=document_id,
        filename=file.filename,
        file_size=file_size,
        file_type=file_extension,
        storage_path=storage_path,
        created_by=current_user["id"],
        comment=comment
    )
    
    # This would be replaced with actual database call
    # db_version = create_document_version(db, version)
    
    # For now, create a dummy response
    version_number = 2  # This would be determined by counting existing versions
    db_version = {
        "id": version_id,
        "document_id": document_id,
        "version_number": version_number,
        "filename": version.filename,
        "file_size": version.file_size,
        "file_type": version.file_type,
        "storage_path": version.storage_path,
        "created_by": version.created_by,
        "comment": version.comment,
        "created_at": datetime.now().isoformat(),
    }
    
    return db_version

@router.get("/", response_model=List[DocumentVersionResponse])
async def get_document_versions(
    document_id: str = Path(...),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get all versions of a document.
    """
    # This would be replaced with actual database calls
    # document = get_document_by_id(db, document_id)
    # if document.owner_id != current_user["id"]:
    #     raise HTTPException(status_code=403, detail="Not authorized to access this document")
    # versions = get_document_versions(db, document_id)
    
    # For now, return dummy data
    versions = [
        {
            "id": "123e4567-e89b-12d3-a456-426614174001",
            "document_id": document_id,
            "version_number": 1,
            "filename": "sample.pdf",
            "file_size": 1024,
            "file_type": "pdf",
            "storage_path": f"{document_id}/versions/123e4567-e89b-12d3-a456-426614174001.pdf",
            "created_by": current_user["id"],
            "comment": "Initial version",
            "created_at": datetime.now().isoformat(),
        }
    ]
    
    return versions

@router.get("/{version_id}", response_model=DocumentVersionResponse)
async def get_document_version(
    document_id: str = Path(...),
    version_id: str = Path(...),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get a specific version of a document.
    """
    # This would be replaced with actual database calls
    # document = get_document_by_id(db, document_id)
    # if document.owner_id != current_user["id"]:
    #     raise HTTPException(status_code=403, detail="Not authorized to access this document")
    # version = get_document_version(db, version_id)
    # if version.document_id != document_id:
    #     raise HTTPException(status_code=404, detail="Version not found for this document")
    
    # For now, return dummy data
    version = {
        "id": version_id,
        "document_id": document_id,
        "version_number": 1,
        "filename": "sample.pdf",
        "file_size": 1024,
        "file_type": "pdf",
        "storage_path": f"{document_id}/versions/{version_id}.pdf",
        "created_by": current_user["id"],
        "comment": "Initial version",
        "created_at": datetime.now().isoformat(),
    }
    
    return version 