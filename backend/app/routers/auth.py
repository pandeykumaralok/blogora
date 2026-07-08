from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserLogin, Token, UserResponse
from app.security import get_password_hash, verify_password, create_access_token, create_refresh_token

router = APIRouter(prefix="/auth", tags=["Authentication Layer"])

@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # Structural verification checks
    email_check = await db.execute(select(User).where(User.email == user_in.email))
    if email_check.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="The email address is already bound to a creator identity.")

    username_check = await db.execute(select(User).where(User.username == user_in.username))
    if username_check.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="This structural username signature is already claimed.")

    # Encrypt Credentials and Mount Base DB Unit
    db_user = User(
        email=user_in.email,
        username=user_in.username,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password)
    )
    db.add(db_user)
    await db.flush() # Extract database identity parameters without final commit wrapper mutation

    return {
        "access_token": create_access_token(subject=db_user.email),
        "refresh_token": create_refresh_token(subject=db_user.email)
    }

@router.post("/login", response_model=Token)
async def login(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_in.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credential parameters provided.")

    return {
        "access_token": create_access_token(subject=user.email),
        "refresh_token": create_refresh_token(subject=user.email)
    }