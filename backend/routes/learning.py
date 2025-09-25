from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import LearningPath, LearningModule, UserLearningPath, User
from ..utils import get_current_user

router = APIRouter()

@router.get("/paths", response_model=List[dict])
async def get_learning_paths(category: str = None, difficulty: str = None, db: Session = Depends(get_db)):
    query = db.query(LearningPath)
    if category:
        query = query.filter(LearningPath.category == category)
    if difficulty:
        query = query.filter(LearningPath.difficulty == difficulty)
    
    paths = query.all()
    return [
        {
            "id": path.id,
            "title": path.title,
            "description": path.description,
            "category": path.category,
            "difficulty": path.difficulty,
            "estimated_hours": path.estimated_hours
        }
        for path in paths
    ]

@router.get("/paths/{path_id}", response_model=dict)
async def get_learning_path(path_id: int, db: Session = Depends(get_db)):
    path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not path:
        raise HTTPException(status_code=404, detail="Learning path not found")
    
    modules = db.query(LearningModule).filter(LearningModule.learning_path_id == path_id).order_by(LearningModule.order).all()
    return {
        "id": path.id,
        "title": path.title,
        "description": path.description,
        "category": path.category,
        "difficulty": path.difficulty,
        "estimated_hours": path.estimated_hours,
        "modules": [
            {
                "id": module.id,
                "title": module.title,
                "content": module.content,
                "module_type": module.module_type,
                "order": module.order,
                "estimated_time": module.estimated_time
            }
            for module in modules
        ]
    }

@router.post("/paths/{path_id}/enroll", response_model=dict)
async def enroll_in_path(path_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == current_user["email"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    existing = db.query(UserLearningPath).filter(UserLearningPath.user_id == user.id, UserLearningPath.learning_path_id == path_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already enrolled")
    
    user_path = UserLearningPath(user_id=user.id, learning_path_id=path_id)
    db.add(user_path)
    db.commit()
    db.refresh(user_path)
    
    return {"message": "Enrolled successfully", "user_path_id": user_path.id}

@router.get("/my-paths", response_model=List[dict])
async def get_my_learning_paths(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == current_user["email"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_paths = db.query(UserLearningPath).filter(UserLearningPath.user_id == user.id).all()
    return [
        {
            "id": up.id,
            "progress": up.progress,
            "started_at": up.started_at,
            "completed_at": up.completed_at,
            "learning_path": {
                "id": up.learning_path.id,
                "title": up.learning_path.title,
                "description": up.learning_path.description,
                "category": up.learning_path.category,
                "difficulty": up.learning_path.difficulty,
                "estimated_hours": up.learning_path.estimated_hours
            }
        }
        for up in user_paths
    ]
