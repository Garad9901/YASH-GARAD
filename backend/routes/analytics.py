from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import QuizAttempt, UserLearningPath, User
from ..utils import get_current_user

router = APIRouter()

@router.get("/quiz-performance", response_model=List[dict])
async def get_quiz_performance(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == current_user["email"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    attempts = db.query(QuizAttempt).filter(QuizAttempt.user_id == user.id).all()
    return [
        {
            "attempt_id": attempt.id,
            "quiz_id": attempt.quiz_id,
            "score": attempt.score,
            "total_questions": attempt.total_questions,
            "correct_answers": attempt.correct_answers,
            "time_taken": attempt.time_taken,
            "completed_at": attempt.completed_at
        }
        for attempt in attempts
    ]

@router.get("/learning-progress", response_model=List[dict])
async def get_learning_progress(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == current_user["email"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_paths = db.query(UserLearningPath).filter(UserLearningPath.user_id == user.id).all()
    return [
        {
            "user_path_id": up.id,
            "learning_path_id": up.learning_path_id,
            "progress": up.progress,
            "started_at": up.started_at,
            "completed_at": up.completed_at
        }
        for up in user_paths
    ]

@router.get("/overall-stats", response_model=dict)
async def get_overall_stats(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == current_user["email"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    quiz_attempts = db.query(QuizAttempt).filter(QuizAttempt.user_id == user.id).count()
    learning_paths = db.query(UserLearningPath).filter(UserLearningPath.user_id == user.id).count()
    average_score = db.query(QuizAttempt.score).filter(QuizAttempt.user_id == user.id).first()
    avg_score = average_score[0] if average_score else 0
    
    return {
        "total_quiz_attempts": quiz_attempts,
        "total_learning_paths": learning_paths,
        "average_quiz_score": avg_score
    }
