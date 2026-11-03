from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.classification import ClassificationCreate, ClassificationRead
from app.services.classification_service import (
    create_classification,
    create_classification_from_upload,
    get_classification,
    list_classifications,
)

router = APIRouter()


@router.post(
    "",
    response_model=ClassificationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Classify Waste Image URL / Reference",
    description="Submits an image reference for AI waste classification, maps the result to a campus waste category, and records the classification event.",
)
def classify_waste_endpoint(
    data: ClassificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ClassificationRead:
    classification = create_classification(db=db, user=current_user, data=data)
    return ClassificationRead.model_validate(classification)


@router.post(
    "/upload",
    response_model=ClassificationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Classify Waste Image File Upload",
    description="Accepts a binary image file or webcam snapshot upload, runs AI classification, and records the event.",
)
def classify_waste_upload_endpoint(
    file: UploadFile = File(..., description="Uploaded image file (JPEG, PNG, WEBP, max 5MB)"),
    disposal_id: Optional[int] = Form(None, description="Optional attached disposal ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ClassificationRead:
    classification = create_classification_from_upload(
        db=db,
        user=current_user,
        file=file,
        disposal_id=disposal_id,
    )
    return ClassificationRead.model_validate(classification)


@router.get(
    "/{classification_id}",
    response_model=ClassificationRead,
    summary="Get Classification by ID",
    description="Retrieves a specific waste classification record. Students and staff can only access their own records; Administrators have platform-wide access.",
)
def get_classification_endpoint(
    classification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ClassificationRead:
    classification = get_classification(
        db=db,
        classification_id=classification_id,
        user=current_user,
    )
    return ClassificationRead.model_validate(classification)


@router.get(
    "",
    response_model=List[ClassificationRead],
    summary="List Classification History",
    description="Lists classification records with pagination. Normal users only view their own history; Administrators view platform-wide submissions.",
)
def list_classifications_endpoint(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[ClassificationRead]:
    classifications = list_classifications(
        db=db,
        user=current_user,
        skip=skip,
        limit=limit,
    )
    return [ClassificationRead.model_validate(c) for c in classifications]
