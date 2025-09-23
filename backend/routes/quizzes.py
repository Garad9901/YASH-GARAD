from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List, Optional
import httpx
import asyncio

from ..database import get_db
from ..models import Quiz, Question, QuizAttempt, UserAnswer, User
from ..config import settings
from ..utils import verify_token

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    email = verify_token(token)
    if email is None:
        raise credentials_exception
    return {"email": email}

@router.get("/", response_model=List[dict])
async def get_quizzes(company: Optional[str] = None, difficulty: Optional[str] = None, category: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Quiz)
    if company:
        query = query.filter(Quiz.company == company)
    if difficulty:
        query = query.filter(Quiz.difficulty == difficulty)
    if category:
        query = query.filter(Quiz.category == category)

    quizzes = query.all()
    return [
        {
            "id": quiz.id,
            "title": quiz.title,
            "description": quiz.description,
            "company": quiz.company,
            "difficulty": quiz.difficulty,
            "category": quiz.category,
            "time_limit": quiz.time_limit,
            "total_questions": quiz.total_questions
        }
        for quiz in quizzes
    ]

@router.get("/{quiz_id}", response_model=dict)
async def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    questions = db.query(Question).filter(Question.quiz_id == quiz_id).all()
    return {
        "id": quiz.id,
        "title": quiz.title,
        "description": quiz.description,
        "company": quiz.company,
        "difficulty": quiz.difficulty,
        "category": quiz.category,
        "time_limit": quiz.time_limit,
        "questions": [
            {
                "id": q.id,
                "question_text": q.question_text,
                "option_a": q.option_a,
                "option_b": q.option_b,
                "option_c": q.option_c,
                "option_d": q.option_d,
                "difficulty": q.difficulty
            }
            for q in questions
        ]
    }

@router.post("/{quiz_id}/submit", response_model=dict)
async def submit_quiz(quiz_id: int, answers: dict, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    # Get quiz and questions
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    questions = db.query(Question).filter(Question.quiz_id == quiz_id).all()

    # Calculate score
    correct_answers = 0
    total_questions = len(questions)

    for question in questions:
        user_answer = answers.get(str(question.id))
        if user_answer and user_answer == question.correct_option:
            correct_answers += 1

    score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0

    # Save attempt
    attempt = QuizAttempt(
        user_id=current_user["id"],
        quiz_id=quiz_id,
        score=score,
        total_questions=total_questions,
        correct_answers=correct_answers,
        time_taken=answers.get("time_taken", 0)
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    # Save individual answers
    for question in questions:
        user_answer = answers.get(str(question.id))
        is_correct = user_answer == question.correct_option if user_answer else False

        answer = UserAnswer(
            attempt_id=attempt.id,
            question_id=question.id,
            selected_option=user_answer,
            is_correct=is_correct
        )
        db.add(answer)

    db.commit()

    return {
        "attempt_id": attempt.id,
        "score": score,
        "correct_answers": correct_answers,
        "total_questions": total_questions,
        "passed": score >= 70  # 70% passing score
    }

@router.post("/coding/submit", response_model=dict)
async def submit_coding_solution(source_code: str, language_id: int, stdin: str = "", current_user: dict = Depends(get_current_user)):
    # Submit to Judge0 API
    judge0_url = f"{settings.judge0_api_url}/submissions"

    payload = {
        "source_code": source_code,
        "language_id": language_id,
        "stdin": stdin
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(judge0_url, json=payload)
        if response.status_code != 201:
            raise HTTPException(status_code=400, detail="Failed to submit to Judge0")

        submission = response.json()
        token = submission["token"]

        # Poll for result
        result_url = f"{settings.judge0_api_url}/submissions/{token}"
        for _ in range(10):  # Poll up to 10 times
            result_response = await client.get(result_url)
            if result_response.status_code == 200:
                result = result_response.json()
                if result["status"]["id"] > 2:  # Not in queue or processing
                    return {
                        "status": result["status"]["description"],
                        "stdout": result.get("stdout", ""),
                        "stderr": result.get("stderr", ""),
                        "compile_output": result.get("compile_output", ""),
                        "passed": result["status"]["id"] == 3  # 3 = Accepted
                    }
            await asyncio.sleep(1)

    raise HTTPException(status_code=408, detail="Submission timed out")
