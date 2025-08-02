from fastapi import FastAPI
from .database import Base, engine
from .routers import auth, chat, user, file, messages
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(user.router)
app.include_router(file.router)
app.include_router(messages.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)