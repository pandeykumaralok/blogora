from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from jose import jwt, JWTError

from app.database import get_db
from app.models import BlogPost, User
from app.schemas import BlogCreate, BlogResponse
from app.config import settings
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/blogs", tags=["Blog Engine"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Helper function to find out which user is making the request using their JWT Token
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate session tokens.",
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user

@router.post("/", response_model=BlogResponse, status_code=status.HTTP_201_CREATED)
async def create_blog(blog_in: BlogCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    new_post = BlogPost(
        title=blog_in.title,
        content=blog_in.content,
        category=blog_in.category,
        read_time=blog_in.read_time,
        user_id=current_user.id
    )
    db.add(new_post)
    await db.flush()
    return new_post

@router.get("/", response_model=List[BlogResponse])
async def get_my_blogs(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BlogPost).where(BlogPost.user_id == current_user.id))
    return result.scalars().all()

@router.put("/{blog_id}", response_model=BlogResponse)
async def update_blog(
    blog_id: int, 
    blog_update: BlogCreate, 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    # Fetch the blog post from the database
    result = await db.execute(select(BlogPost).where(BlogPost.id == blog_id))
    blog = result.scalar_one_or_none()
    
    if blog is None:
        raise HTTPException(status_code=404, detail="Article not found.")
        
    # Security Check: Ensure the logged-in user actually owns this blog post!
    if blog.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this article.")
        
    # Update the values
    blog.title = blog_update.title
    blog.content = blog_update.content
    blog.category = blog_update.category
    blog.read_time = blog_update.read_time
    
    await db.commit()
    await db.refresh(blog)
    return blog

@router.get("/public", response_model=List[BlogResponse])
async def get_public_feed(db: AsyncSession = Depends(get_db)):
    """
    Publicly lists all blog articles in the database.
    Perfect for the end-user feed page.
    """
    result = await db.execute(select(BlogPost).order_by(BlogPost.created_at.desc()))
    return result.scalars().all()