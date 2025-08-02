from requests import Session
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from app.database import get_db
from ..oauth2 import get_current_user
from .. import models
from app import schemas

router = APIRouter(tags=['Chat'])


@router.delete("/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(message_id: int, 
                   db: Session = Depends(get_db), 
                   username: str = Depends(get_current_user)):
    
    user = db.query(models.User).filter(models.User.email == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    message = db.query(models.Message).filter(
        models.Message.id == message_id,
        models.Message.chat.has(user_id=user.id)
    ).first()

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Check if the user owns the chat that this message belongs to
    chat = db.query(models.Chat).filter(models.Chat.id == message.chat_id).first()
    if not chat or chat.user.email != username:
        raise HTTPException(status_code=403, detail="Not authorized to delete this message")
    
    db.delete(message)
    db.commit()

    return {"message": "Message deleted successfully"}

@router.patch("/{chat_id}/messages/{message_id}")
def update_message(
    chat_id: int,
    message_id: int,
    request: schemas.ChatRequest,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    # Verify user exists
    user = db.query(models.User).filter(models.User.email == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify chat belongs to user
    chat = db.query(models.Chat).filter(
        models.Chat.id == chat_id,
        models.Chat.user_id == user.id
    ).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Verify message exists in chat
    message = db.query(models.Message).filter(
        models.Message.id == message_id,
        models.Message.chat_id == chat.id
    ).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    # Update the message content
    message.content = request.message
    db.commit()
    db.refresh(message)

    return {
        "message": "Message updated successfully",
        "updated_content": message.content
    }
