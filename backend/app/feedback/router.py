from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import json
import os
import datetime as dt

router = APIRouter(prefix="/feedback", tags=["feedback"])

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
FEEDBACK_PATH = os.path.join(DATA_DIR, "feedback.jsonl")


class FeedbackRequest(BaseModel):
	sample_id: str
	user_label: str
	notes: Optional[str] = None
	text: Optional[str] = None


class FeedbackResponse(BaseModel):
	status: str


@router.post("", response_model=FeedbackResponse)
async def submit_feedback(body: FeedbackRequest) -> FeedbackResponse:
	os.makedirs(DATA_DIR, exist_ok=True)
	record = {
		"timestamp": dt.datetime.utcnow().isoformat() + "Z",
		"sample_id": body.sample_id,
		"user_label": body.user_label,
		"notes": body.notes,
		"text": body.text,
	}
	with open(FEEDBACK_PATH, "a", encoding="utf-8") as f:
		f.write(json.dumps(record, ensure_ascii=False) + "\n")
	return FeedbackResponse(status="ok")