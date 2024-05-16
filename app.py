
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File,status
from dotenv import load_dotenv
import os
import uvicorn
from pydantic import BaseModel, Field
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy import func
from face_detection import detect_face
import cv2
import mediapipe as mp
from tempfile import NamedTemporaryFile
from io import BytesIO
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from utils import get_hashed_password,verify_password,create_access_token,create_refresh_token
from cachetools import cached, TTLCache
from uuid import uuid4
import numpy as np



app = FastAPI()
models.Base.metadata.create_all(bind=engine)

cache = TTLCache(maxsize=100, ttl=300)


def get_cache_key(*args, **kwargs):
    """
    Generate a cache key using the provided arguments and keyword arguments.

    Args:
        *args: Positional arguments.
        **kwargs: Keyword arguments.

    Returns:
        str: The generated cache key.
    """
    return str(args) + str(kwargs)


def get_db():   
    """
    Create a new database session and yield it.

    Yields:
        Session: A database session.
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class User(BaseModel):
    """
    Pydantic model representing a user.

    Attributes:
        name (str): The name of the user.
        password (str): The password of the user.
    """
    name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=5, max_length=50)


class TokenSchema(BaseModel):
    """
    Pydantic model representing a token.

    Attributes:
        access_token (str): The access token.
        refresh_token (str): The refresh token.
    """
    access_token: str
    refresh_token: str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


users = []

  
def authenticate_user(name: str, password: str,db: Session=Depends(get_db)):
    """
    Authenticate a user with the provided name and password.

    Args:
        name (str): The name of the user.
        password (str): The password of the user.
        db (Session): The database session.

    Returns:
        User: The authenticated user if successful, None otherwise.
    """
    user = db.query(models.User).filter(func.lower(models.User.name) == func.lower(name)).first()
    if not user or not verify_password(password, user.password):
        return None
    return user


@app.get("/", summary="Root endpoint",)
async def root(db: Session = Depends(get_db)):
    """
    Root endpoint returning a  list of users.
    """
    users = db.query(models.User).all()
    user_names = [user.name for user in users]
    return {"user_names": user_names}
    


@app.post("/create",summary="Create new user")
def create_user(user: User, db: Session = Depends(get_db)):
    """
    Create a new user.

    Args:
        user (User): The user details.
        db (Session): The database session.

    Returns:
        User: The created user.
    """
    user_model = models.User()
    user_model.name = user.name
    user_model.password = get_hashed_password(user.password)

    db.add(user_model)
    db.commit()

    return user_model

@app.post('/login', summary="Create access and refresh tokens for user", response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login endpoint to authenticate users and generate access and refresh tokens.

    Args:
        form_data (OAuth2PasswordRequestForm): Form data containing the username and password.
        db (Session): The database session.

    Returns:
        dict: A dictionary containing the access and refresh tokens.
    """
    user = authenticate_user(db,form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    access_token = create_access_token(user.name)
    refresh_token = create_refresh_token(user.name)
    return {"access_token": access_token, "refresh_token": refresh_token}



@app.put("/{user_id}")
@cached(cache, key=get_cache_key)
def update_user(user_id: int, user: User, db: Session = Depends(get_db)):
    """
    Update a user by ID.

    Args:
        user_id (int): The ID of the user to update.
        user (User): The updated user details.
        db (Session): The database session.

    Returns:
        User: The updated user.
    """
    user_model = db.query(models.User).filter(models.User.id == user_id).first()

    if user_model is None:
        raise HTTPException(
            status_code=404, detail=f"ID {user_id} : Does not exist in database"
        )

    user_model.name = user.name

    db.add(user_model)
    db.commit()

    return user



@app.post("/search")
def search_by_name(name_to_search: str, user: User, db: Session = Depends(get_db)):
    """
    Search for users by name.

    Args:
        name_to_search (str): The name to search for.
        user (User): The user details.
        db (Session): The database session.

    Returns:
        list: A list of users matching the search criteria.
    """
    
    user_model = db.query(models.User).filter(models.User.name == name_to_search).all()
    user_model = (
        db.query(models.User)
        .filter(func.lower(models.User.name).like(func.lower(f"%{name_to_search}%")))
        .all()
    )

    if user_model is None:
        raise HTTPException(
            status_code=404, detail=f"User with name '{name_to_search}' not found"
        )

    return user_model


@app.post("/process_image/")
async def process_image(file: UploadFile = File(...)):
    """
    Process an uploaded image by detecting faces and returning the processed image.

    Args:
        file (UploadFile): The uploaded image file.

    Returns:
        FileResponse: The processed image file response.
    """
    try:
        # Read the uploaded image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Call the face detection and processing function
        result_image, cropped_face = detect_face(image)

        # Save the processed image temporarily
        temp_file = NamedTemporaryFile(delete=False, suffix=".jpg")
        cv2.imwrite(temp_file.name, result_image)
        cv2.imwrite(temp_file.name, cropped_face)

        # Return the processed image
        return FileResponse(temp_file.name, media_type="image/jpeg")

    except Exception as e:
        return {"error": str(e)}

    

if __name__ == "_main_":
    uvicorn.run(app, host="0.0.0.0", port=8000)