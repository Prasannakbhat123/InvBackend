from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, require_admin
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import UserTable
from app.core.id_generator import generate_user_id
from app.schemas.auth_schema import LoginRequest, TokenResponse, RegisterRequest

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(UserTable).filter(UserTable.user_username == payload.user_username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username")

    if not verify_password(payload.user_password, user.user_password):
        raise HTTPException(status_code=401, detail="Invalid password")

    token = create_access_token({"user_id": user.user_id, "role": user.role})

    return TokenResponse(
        access_token=token,
        role=user.role,
        user_id=user.user_id
    )
#for testing only
@router.post("/register")
def register_user(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
    admin_user: UserTable = Depends(require_admin)
):
    if payload.role not in ["admin", "employee"]:
        raise HTTPException(status_code=400, detail="Role must be admin or employee")

    existing = db.query(UserTable).filter(UserTable.user_username == payload.user_username).first()
    if existing:
        raise HTTPException(status_code=409, detail="Username already exists")

    new_user_id = generate_user_id(db, payload.role)
    user = UserTable(
        user_id=new_user_id,
        user_username=payload.user_username,
        user_password=hash_password(payload.user_password),
        role=payload.role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User registered successfully ", "user_id": user.user_id, "role": user.role}

@router.get("/me")
def me(current_user: UserTable = Depends(get_current_user)):
    return {
        "user_id": current_user.user_id,
        "user_username": current_user.user_username,
        "role": current_user.role,
        "created_at": current_user.created_at
    }
