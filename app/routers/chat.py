from requests import Session, request
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from app.database import get_db
from ..oauth2 import get_current_user
from ..schemas import ChatRequest, ChatUpdate
from .. import models
from app import schemas

router = APIRouter(tags=['Chat'])

@router.post("/send/{chat_id}")
def chat(request: ChatRequest, chat_id: int, 
         db: Session = Depends(get_db), 
         username: str = Depends(get_current_user)):
    
    user = db.query(models.User).filter(
        models.User.email == username
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # chat_id is always provided now
    chat = db.query(models.Chat).filter(
        models.Chat.id == chat_id,
        models.Chat.user_id == user.id
    ).first()

    # Save user's message
    user_message = models.Message(
        chat_id=chat.id,
        sender="user",
        content=request.message,
    )
    db.add(user_message)
    chat.updated_at = func.now()
    db.commit()

    # Send message to the LLM
    llm = ChatOllama(
        model="llama3:8b",
        temperature=0.7
    )
    messages = [HumanMessage(request.message)]
    llm_response = llm.invoke(messages).content

    # Save bot's response
    bot_message = models.Message(
        chat_id=chat.id,
        sender="assistant",
        content=llm_response,
    )
    db.add(bot_message)
    chat.updated_at = func.now()
    db.commit()

    return {"reply": llm_response}

@router.post("/chats", response_model=schemas.ChatOut)
def create_chat(db: Session = Depends(get_db), 
                username: str = Depends(get_current_user)):
    user = db.query(models.User).filter(
        models.User.email == username
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_chat = models.Chat(user_id=user.id)
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)

    return new_chat

@router.get("/chats", response_model=list[schemas.ChatOutDetail])
def get_chats(db: Session = Depends(get_db), 
              username: str = Depends(get_current_user)):
    
    user = db.query(models.User).filter(models.User.email == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    chats = (db.query(models.Chat).filter(
        models.Chat.user_id == user.id
    ).order_by(models.Chat.updated_at.desc()).all())
    
    return chats


@router.get("/chats/{chat_id}", response_model=schemas.ChatOutDetail)
def get_chat(chat_id: int, db: Session = Depends(get_db), 
             username: str = Depends(get_current_user)):
    
    user = db.query(models.User).filter(models.User.email == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    chat = db.query(models.Chat).filter(
        models.Chat.id == chat_id,
        models.Chat.user_id == user.id
    ).first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    return chat

@router.patch("/chats/{chat_id}")
def update_chat(chat_id: int, 
                chat_update: ChatUpdate, 
                db: Session = Depends(get_db), 
                username: str = Depends(get_current_user)):
    
    user = db.query(models.User).filter(models.User.email == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    chat = db.query(models.Chat).filter(
        models.Chat.id == chat_id, 
        models.Chat.user_id == user.id
    ).first()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    chat.title = chat_update.title

    chat.updated_at = func.now()
    db.commit()
    db.refresh(chat)

    return chat

@router.delete("/chats/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat(chat_id: int, 
                db: Session = Depends(get_db), 
                username: str = Depends(get_current_user)):
    
    user = db.query(models.User).filter(models.User.email == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    chat = db.query(models.Chat).filter(
        models.Chat.id == chat_id, 
        models.Chat.user_id == user.id
    ).first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    db.delete(chat)
    db.commit()

    return {"message": "Chat deleted successfully"}

@router.post("/chats/{chat_id}/regenerate")
def regenerate_response(chat_id: int,
                        db: Session = Depends(get_db),
                        username: str = Depends(get_current_user)):

    user = db.query(models.User).filter(models.User.email == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    chat = db.query(models.Chat).filter(
        models.Chat.id == chat_id,
        models.Chat.user_id == user.id
    ).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    last_user_msg = (
        db.query(models.Message)
        .filter(models.Message.chat_id == chat.id, models.Message.sender == "user")
        .order_by(models.Message.created_at.desc())
        .first()
    )
    if not last_user_msg:
        raise HTTPException(status_code=404, detail="No user message found to regenerate")
    
    last_ai_msg = (
        db.query(models.Message)
        .filter(models.Message.chat_id == chat.id, models.Message.sender == "assistant")
        .order_by(models.Message.created_at.desc())
        .first()
    )
    if last_ai_msg:
        db.delete(last_ai_msg)
        db.commit()

    llm = ChatOllama(
        model="llama3:8b",
        temperature=0.7
    )
    messages = [HumanMessage(last_user_msg.content)]
    regenerated_reply = llm.invoke(messages).content

    new_ai_msg = models.Message(
        chat_id=chat.id,
        sender="assistant",
        content=regenerated_reply,
    )
    db.add(new_ai_msg)
    db.commit()
    db.refresh(new_ai_msg)

    return {"reply": regenerated_reply, "message_id": new_ai_msg.id}

@router.post("/chats/{chat_id}/continue")
def continue_chat(
    chat_id: int,
    request: schemas.ChatRequest,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    # Validate user
    user = db.query(models.User).filter(models.User.email == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Validate chat
    chat = db.query(models.Chat).filter(
        models.Chat.id == chat_id,
        models.Chat.user_id == user.id
    ).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Fetch last N messages for context
    messages = db.query(models.Message).filter(
        models.Message.chat_id == chat.id
    ).order_by(models.Message.created_at.asc()).all()

    # Build chat history for LLM
    history = []
    for msg in messages:
        if msg.sender == "user":
            history.append(HumanMessage(msg.content))
        else:
            history.append(SystemMessage(msg.content))

    # Append the user's new message
    history.append(HumanMessage(request.message))

    # Get LLM response
    llm = ChatOllama(
        model="llama3:8b",  # Same model OpenWebUI uses
        temperature=0.7
    )
    llm_response = llm.invoke(history).content

    # Save user message
    user_message = models.Message(
        chat_id=chat.id,
        sender="user",
        content=request.message
    )
    db.add(user_message)

    # Save assistant message
    bot_message = models.Message(
        chat_id=chat.id,
        sender="assistant",
        content=llm_response
    )
    db.add(bot_message)

    # Update chat timestamp
    chat.updated_at = func.now()
    db.commit()

    return {
        "reply": llm_response,
        "chat_id": chat.id,
        "messages": [
            {"id": msg.id, "sender": msg.sender, "content": msg.content}
            for msg in messages
        ] + [
            {"id": user_message.id, "sender": "user", "content": request.message},
            {"id": bot_message.id, "sender": "assistant", "content": llm_response},
        ]
    }
