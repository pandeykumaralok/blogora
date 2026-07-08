from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserLogin, Token, UserResponse
from app.routers.blogs import get_current_user
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

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
import os
import uuid

# Define where files go relative to your project execution folder
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.put("/update-avatar")
async def update_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. Validate file extension type to ensure security
    extension = os.path.splitext(file.filename)[1].lower()
    if extension not in [".jpg", ".jpeg", ".png", ".webp"]:
        raise HTTPException(
            status_code=400, 
            detail="Invalid image structure. Allowed formats: JPG, PNG, WEBP."
        )
    
    # 2. Forge a unique, randomized filename to prevent overwriting other users' avatars
    unique_filename = f"{uuid.uuid4()}{extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # 3. Read the binary chunks and stream them onto the hard drive disk safely
    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to write file to storage engine matrix.")
    
    # 4. Generate the clean download route URL address string point
    public_url = f"http://127.0.0.1:8080/static/uploads/{unique_filename}"
    
    # 5. Commit the database record
    current_user.profile_pic = public_url
    await db.commit()
    
    return {"message": "Avatar uploaded successfully!", "profile_pic": public_url}

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Returns the currently authenticated user's details, including their profile picture path.
    """
    return current_user