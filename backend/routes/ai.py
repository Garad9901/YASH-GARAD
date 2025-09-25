from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
try:
    import tensorflow as tf
    import numpy as np
except ImportError:
    tf = None
    np = None
from ..database import get_db
from ..models import QuizAttempt, User
from ..utils import get_current_user

router = APIRouter()

# Simple AI model for adaptive learning (placeholder)
def get_adaptive_recommendations(user_id: int, db: Session):
    # This is a placeholder - in real implementation, use ML models
    attempts = db.query(QuizAttempt).filter(QuizAttempt.user_id == user_id).all()
    if not attempts:
        return {"recommendation": "Start with basic quizzes"}
    
    avg_score = np.mean([a.score for a in attempts])
    if avg_score > 80:
        return {"recommendation": "Try advanced topics"}
    elif avg_score > 50:
        return {"recommendation": "Practice more intermediate quizzes"}
    else:
        return {"recommendation": "Focus on basic concepts"}

@router.get("/recommendations", response_model=dict)
async def get_recommendations(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == current_user["email"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    recommendations = get_adaptive_recommendations(user.id, db)
    return recommendations

@router.post("/plagiarism-check", response_model=dict)
async def check_plagiarism(text: str, current_user: dict = Depends(get_current_user)):
    # Placeholder for plagiarism detection
    # In real implementation, use NLP models to compare with known sources
    if len(text) < 100:
        return {"plagiarism_score": 0.1, "message": "Text too short for accurate check"}
    
    # Simple heuristic: check for repeated phrases
    words = text.split()
    unique_words = set(words)
    plagiarism_score = 1 - (len(unique_words) / len(words)) if words else 0
    
    return {
        "plagiarism_score": min(plagiarism_score, 1.0),
        "message": "High score indicates potential plagiarism"
    }
