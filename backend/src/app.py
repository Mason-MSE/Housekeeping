from pathlib import Path
import importlib.util
import sys
from typing import List, Optional
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from core.dependencies import get_current_user
from api.auth import auth_router
from api.portal import router as portal_router
from api.rbac import router as rbac_router
from init_db import init_database


app = FastAPI(
    title="Housekeeping System",
    description="Hotel Housekeeping Management System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def include_routers_from_folder(folder: str = "api"):
    """Include all routers from a folder."""
    routers_path = Path(__file__).parent / folder

    skip_modules = ["car", "booking", "insurance", "role_resource", "user_role", "service_detail", 
                    "inspection", "other", "cleaner_application"]

    for file_path in routers_path.glob("*.py"):
        if file_path.name == "__init__.py" or file_path.name == "auth.py":
            continue
        
        module_name = file_path.stem
        if module_name in skip_modules:
            continue

        spec = importlib.util.spec_from_file_location(f"app.{folder}.{module_name}", file_path)
        if spec is None or spec.loader is None:
            continue

        module = importlib.util.module_from_spec(spec)
        sys.modules[f"app.{folder}.{module_name}"] = module
        spec.loader.exec_module(module)

        if hasattr(module, "router"):
            router = getattr(module, "router")
            app.include_router(router, dependencies=[Depends(get_current_user)])

        if hasattr(module, "public_router"):
            app.include_router(module.public_router)


app.include_router(auth_router)
app.include_router(portal_router)
app.include_router(rbac_router)
include_routers_from_folder("api")

@app.get("/health")
async def root():
    """"Health check endpoint to verify that the application is running."""
    return {"message": "<p style='color:blue;'>Welcome to Housekeeping Management System</p>"}

@app.on_event("startup")
def startup_event():
    """"Initialize the database connection on application startup."""
    init_database()


# @app.get("/pic/{id}")
# def output_pic(id: int):
#     """Test endpoint to verify that static files are served correctly."""
#     img_path = Path(__file__).parent / "static" / f"{id}.jpg"
#     print(f"Attempting to serve image from: {img_path}")
#     if not img_path.is_file():
#         raise HTTPException(status_code=404, detail="Image not found")

#     return FileResponse(img_path, media_type="image/jpeg")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
