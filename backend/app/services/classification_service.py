import base64
import logging
from decimal import Decimal
from pathlib import Path
from typing import List, Optional
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ai.classification.classifier import BaseWasteClassifier
from ai.classification.model import MockWasteClassifier
from ai.classification.preprocessing import ImageValidationError, validate_image_reference
from app.core.config import settings
from app.models.classification import WasteClassification
from app.models.disposal import DisposalRecord
from app.models.user import User
from app.models.waste_type import WasteType
from app.schemas.classification import ClassificationCreate

logger = logging.getLogger(__name__)

ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/jpg",
    "application/octet-stream",  # Fallback for binary blob transfers from webcams
}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

_classifier_instance: Optional[BaseWasteClassifier] = None


def get_classifier() -> BaseWasteClassifier:
    """Retrieve or initialize the active classifier implementation.

    Initializes FastAIWasteClassifier if the model checkpoint exists and FastAI is available;
    gracefully falls back to MockWasteClassifier for testing or offline environments.
    """
    global _classifier_instance
    if _classifier_instance is None:
        model_path = Path(settings.CLASSIFICATION_MODEL_PATH)
        if not model_path.is_absolute():
            if not model_path.exists():
                candidate = Path(__file__).resolve().parent.parent.parent.parent / model_path
                if candidate.exists():
                    model_path = candidate

        if model_path.exists() and model_path.suffix == ".pkl":
            try:
                from ai.classification.fastai_model import FastAIWasteClassifier

                _classifier_instance = FastAIWasteClassifier(
                    model_path=model_path,
                    model_version=settings.CLASSIFICATION_MODEL_VERSION,
                    confidence_threshold=settings.CLASSIFICATION_CONFIDENCE_THRESHOLD,
                )
                logger.info("Successfully loaded FastAIWasteClassifier from %s", model_path)
            except Exception as exc:
                logger.warning(
                    "Could not load FastAI model from %s (%s). Falling back to MockWasteClassifier.",
                    model_path,
                    exc,
                )
                _classifier_instance = MockWasteClassifier(
                    model_version=settings.CLASSIFICATION_MODEL_VERSION,
                    confidence_threshold=settings.CLASSIFICATION_CONFIDENCE_THRESHOLD,
                )
        else:
            _classifier_instance = MockWasteClassifier(
                model_version=settings.CLASSIFICATION_MODEL_VERSION,
                confidence_threshold=settings.CLASSIFICATION_CONFIDENCE_THRESHOLD,
            )
    return _classifier_instance


def set_classifier(classifier: Optional[BaseWasteClassifier]) -> None:
    """Explicitly set or override the active classifier (useful for tests and model swapping)."""
    global _classifier_instance
    _classifier_instance = classifier


def create_classification(
    db: Session,
    user: User,
    data: ClassificationCreate,
) -> WasteClassification:
    """Validate image reference, run inference through classifier, map to waste type, and persist record."""
    # 1. Validate image reference
    try:
        sanitized_image_url = validate_image_reference(data.image_url)
    except ImageValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    # 2. If disposal_id is attached, verify ownership and existence
    if data.disposal_id is not None:
        disposal = (
            db.query(DisposalRecord)
            .filter(DisposalRecord.disposal_id == data.disposal_id)
            .first()
        )
        if not disposal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Referenced disposal record not found.",
            )

        user_role = user.role.role_name.upper() if user.role else ""
        if user_role != "ADMIN" and disposal.user_id != user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot attach classification to another user's disposal record.",
            )

    # 3. Perform inference via the classifier interface
    classifier = get_classifier()
    prediction = classifier.classify(sanitized_image_url)

    # 4. Map predicted class to active campus WasteType
    waste_type = (
        db.query(WasteType)
        .filter(
            WasteType.name == prediction.predicted_class,
            WasteType.is_active == True,
        )
        .first()
    )
    if not waste_type:
        raise HTTPException(
            status_code=422,
            detail=f"Predicted waste category '{prediction.predicted_class}' cannot be mapped to an active campus waste type.",
        )

    # 5. Format confidence score
    conf_decimal: Optional[Decimal] = None
    if prediction.confidence_score is not None:
        conf_decimal = Decimal(str(round(prediction.confidence_score, 4)))

    # 6. Save WasteClassification record
    classification = WasteClassification(
        user_id=user.user_id,
        disposal_id=data.disposal_id,
        image_url=sanitized_image_url,
        predicted_waste_type_id=waste_type.waste_type_id,
        confidence_score=conf_decimal,
        model_version=prediction.model_version,
    )
    db.add(classification)
    db.commit()
    db.refresh(classification)
    return classification


def get_classification(
    db: Session,
    classification_id: int,
    user: User,
) -> WasteClassification:
    """Retrieve an individual classification record with ownership verification."""
    classification = (
        db.query(WasteClassification)
        .filter(WasteClassification.classification_id == classification_id)
        .first()
    )
    if not classification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classification record not found.",
        )

    user_role = user.role.role_name.upper() if user.role else ""
    if user_role != "ADMIN" and classification.user_id != user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You do not have permission to view this classification record.",
        )

    return classification


def list_classifications(
    db: Session,
    user: User,
    skip: int = 0,
    limit: int = 20,
) -> List[WasteClassification]:
    """List classification records with pagination. Normal users only view their own history; admins view platform-wide."""
    query = db.query(WasteClassification)

    user_role = user.role.role_name.upper() if user.role else ""
    if user_role != "ADMIN":
        query = query.filter(WasteClassification.user_id == user.user_id)

    return (
        query.order_by(WasteClassification.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_classification_from_upload(
    db: Session,
    user: User,
    file: UploadFile,
    disposal_id: Optional[int] = None,
) -> WasteClassification:
    """Validate uploaded multipart file, encode safe data URI representation, and execute classification."""
    content_type = (file.content_type or "image/jpeg").lower().strip()
    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{content_type}'. Allowed formats: JPEG, PNG, WEBP.",
        )

    try:
        content = file.file.read(MAX_FILE_SIZE + 1)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read uploaded image stream: {exc}",
        )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds maximum allowable limit of 5 MB.",
        )
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    # Use original filename extension or derive from content type for data URI
    mime = "image/jpeg" if content_type == "application/octet-stream" else content_type
    b64_str = base64.b64encode(content).decode("utf-8")
    data_uri = f"data:{mime};base64,{b64_str}"

    return create_classification(
        db=db,
        user=user,
        data=ClassificationCreate(
            image_url=data_uri,
            disposal_id=disposal_id,
        ),
    )
