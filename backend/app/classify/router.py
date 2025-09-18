from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from ..ml.text_classifier import get_text_classifier, MODEL_VERSION

router = APIRouter(prefix="/classify", tags=["classify"])


class ClassifyRequest(BaseModel):
    text: str | None = None


class Highlight(BaseModel):
    token: str
    score: float


class ClassifyResponse(BaseModel):
    label: str
    confidence: float
    reasons: List[str]
    highlights: List[Highlight]
    model_version: str
    latency_ms: int


@router.post("", response_model=ClassifyResponse)
def classify(req: ClassifyRequest) -> ClassifyResponse:
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="text is required")

    classifier = get_text_classifier()
    result = classifier.predict(req.text)

    label_norm = result.label.lower()
    if label_norm in ("true", "genuine"):
        label_norm = "real"

    return ClassifyResponse(
        label=label_norm,
        confidence=result.confidence,
        reasons=result.reasons,
        highlights=[Highlight(token=t, score=s) for t, s in result.token_importances],
        model_version=MODEL_VERSION,
        latency_ms=result.latency_ms,
    )