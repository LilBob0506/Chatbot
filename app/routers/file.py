import os
from uuid import uuid4
from fastapi.responses import FileResponse
from requests import Session
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from app.database import get_db
from ..oauth2 import get_current_user
from .. import models
from fastapi import File, UploadFile

router = APIRouter(tags=['File'])

@router.post("/upload/{chat_id}")
async def upload_file(chat_id: int,
                      file: UploadFile = File(...), 
                      db: Session = Depends(get_db),
                      username: str = Depends(get_current_user)):
    
    # Check user
    user = db.query(models.User).filter(models.User.email == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check chat
    chat = db.query(models.Chat).filter(
        models.Chat.id == chat_id,
        models.Chat.user_id == user.id
    ).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Ensure uploads folder exists
    uploads_dir = "uploads"
    os.makedirs(uploads_dir, exist_ok=True)

    # Generate safe file name to avoid collisions
    file_ext = os.path.splitext(file.filename)[1]
    safe_filename = f"{chat_id}_{uuid4().hex}{file_ext}"
    file_location = os.path.join(uploads_dir, safe_filename)

    # Save file to disk
    with open(file_location, "wb") as f:
        content = await file.read()
        f.write(content)

    # Save a reference in the DB
    file_message = models.Message(
        chat_id=chat.id,
        sender="user",
        content=f"[file:{file_location}]",  # Store file path or a custom tag
    )
    db.add(file_message)
    db.commit()
    db.refresh(file_message)

    return {
        "message": "File uploaded successfully",
        "file_path": file_location,
        "message_id": file_message.id
    }

@router.get("/files/{file_id}")
async def get_file(file_id: int,
                   db: Session = Depends(get_db),
                   username: str = Depends(get_current_user)):
    
     # Get user
    user = db.query(models.User).filter(models.User.email == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get message with file
    message = db.query(models.Message).filter(
        models.Message.id == file_id,
        models.Message.sender == "user"  # Ensure it's a user-uploaded file
    ).first()

    if not message or not message.content.startswith("[file:"):
        raise HTTPException(status_code=404, detail="File not found")

    # Extract file path
    file_path = message.content[6:-1]  # Removes "[file:" and "]"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File does not exist on server")

    # Serve the file
    return FileResponse(path=file_path, 
                        filename=os.path.basename(file_path))
