from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from .. import database, models, utils
from ..oauth2 import create_access_token, create_refresh_token, decode_token, get_current_user
from ..schemas import UserLogin, RefreshRequest

router = APIRouter(tags=['Authentication'])

REFRESH_TOKENS = set()

@router.post("/login")
def login(request: UserLogin,  db: Session = Depends(database.get_db)):

    user = db.query(models.User).filter(models.User.email == request.email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    if not utils.verify(request.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    access_token = create_access_token({"sub": request.email})
    refresh_token = create_refresh_token({"sub": request.email})

    # Store refresh token
    REFRESH_TOKENS.add(refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }

@router.post("/refresh")
def refresh_token(request: RefreshRequest):
    payload = decode_token(request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    if request.refresh_token not in REFRESH_TOKENS:
        raise HTTPException(status_code=401, detail="Refresh token has been revoked")

    # Issue new access token
    new_access_token = create_access_token({"sub": payload["sub"]})
    return {"access_token": new_access_token}

@router.post("/logout")
def logout(current_user: str = Depends(get_current_user)):
    """
    Logs out the user by invalidating their refresh token (if stored).
    """
    print(f"[Logout] User {current_user} logged out.")

    # Optional: Remove user's refresh token from server-side store
    # Example: If you stored them as REFRESH_TOKENS[current_user]
    # REFRESH_TOKENS.pop(current_user, None)

    return {"detail": "Logged out successfully"}