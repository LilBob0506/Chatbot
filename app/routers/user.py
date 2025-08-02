from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session

from app.oauth2 import get_current_user
from .. import models, schemas, utils
from ..database import get_db


router = APIRouter(tags=['Users'])

@router.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, 
                db: Session = Depends(get_db)):
    
    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, 
                            detail="Email already registered")

    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"detail": "User registered successfully"}

@router.get("/users/me", response_model=schemas.UserOut)
def get_current_user_details(db: Session = Depends(get_db),
                             current_user: str = Depends(get_current_user)):

    user = db.query(models.User).filter(
        models.User.email == current_user
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

@router.patch("/users/me", response_model=schemas.UserOut)
def update_my_account(update: schemas.UserUpdate, 
                      db: Session = Depends(get_db), 
                      username: str = Depends(get_current_user)):
    
    user = db.query(models.User).filter(
        models.User.email == username
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if update.email:
        user.email = update.email
    if update.password:
        hashed_password = utils.hash(update.password)
        user.password = hashed_password

    db.commit()
    db.refresh(user)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Account updated. Please log in again with your new credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

@router.get("/stats")
def get_user_stats(
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    # Get user
    user = db.query(models.User).filter(models.User.email == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Count chats
    chat_count = db.query(models.Chat).filter(models.Chat.user_id == user.id).count()

    # Count messages
    message_count = (
        db.query(models.Message)
        .join(models.Chat)
        .filter(models.Chat.user_id == user.id)
        .count()
    )

    # Find most recent activity
    last_message = (
        db.query(models.Message)
        .join(models.Chat)
        .filter(models.Chat.user_id == user.id)
        .order_by(models.Message.created_at.desc())
        .first()
    )
    last_activity = last_message.created_at if last_message else None

    return {
        "total_chats": chat_count,
        "total_messages": message_count,
        "last_activity": last_activity,
        "user": user.email,
    }
