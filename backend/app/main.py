import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config import settings
from app.database import engine, Base
from app.routers import auth, blogs

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# 1. Mount API Router endpoints first
app.include_router(auth.router, prefix="/api")
app.include_router(blogs.router, prefix="/api")

# 2. Map the absolute path to your frontend folder
# Assumes 'frontend' is a sibling folder to your 'backend' folder
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend"))

# 3. Mount all assets inside css/ and js/ folders 
if os.path.exists(FRONTEND_DIR):
    app.mount("/css", StaticFiles(directory=os.path.join(FRONTEND_DIR, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="js")

    # 4. Bind the root landing URL to serve your index.html file directly
    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

    # 5. Bind explicit HTML routes for auth and dashboard pages
    @app.get("/auth.html")
    async def serve_auth():
        return FileResponse(os.path.join(FRONTEND_DIR, "auth.html"))

    @app.get("/dashboard.html")
    async def serve_dashboard():
        return FileResponse(os.path.join(FRONTEND_DIR, "dashboard.html"))

    @app.get("/feed.html")
    async def serve_feed():
        return FileResponse(os.path.join(FRONTEND_DIR, "feed.html"))

# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from app.config import settings
# from app.database import engine, Base
# from app.routers import auth

# app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

# # Setup CORS Policy configuration mapping your local web servers cleanly
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Swap out explicitly with production domains later
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.on_event("startup")
# async def startup():
#     # Structural DB Core Schema Initialization
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)

# # Append Mounted Subsystem Routers
# app.include_router(auth.router, prefix="/api")

# @app.get("/api/health", tags=["System System Diagnostic Check"])
# def health_check():
#     return {"status": "operational", "engine": "Aura Premium Platform Service"}