from passlib.context import CryptContext
import os
from dotenv import load_dotenv

from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt

load_dotenv()
ACCESS_TOKEN_EXPIRE_MINUTES = 30  #  minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']   
JWT_REFRESH_SECRET_KEY = os.environ['JWT_REFRESH_SECRET_KEY'] 

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password: str) -> str:
    """
    Hashes the provided password using bcrypt.

    Args:
        password (str): The password to be hashed.

    Returns:
        str: The hashed password.
    """ 
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    """
    Verifies if the provided password matches the hashed password.

    Args:
        password (str): The password to be verified.
        hashed_pass (str): The hashed password stored in the database.

    Returns:
        bool: True if the password matches the hashed password, False otherwise.
    """
    return password_context.verify(password, hashed_pass)

def create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    
    """
    Creates an access token for the provided subject.

    Args:
        subject (Union[str, Any]): The subject for whom the token is being created.
        expires_delta (int, optional): The expiration time delta for the token. Defaults to None.

    Returns:
        str: The JWT access token.
    """
    if expires_delta is not None:
        expires_delta = datetime.now(datetime.UTC) + expires_delta
    else:
        expires_delta = datetime.now(datetime.UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    """
    Creates a refresh token for the provided subject.

    Args:
        subject (Union[str, Any]): The subject for whom the token is being created.
        expires_delta (int, optional): The expiration time delta for the token. Defaults to None.

    Returns:
        str: The JWT refresh token.
    """
    if expires_delta is not None:
        expires_delta = datetime.now(datetime.UTC) + expires_delta
    else:
        expires_delta = datetime.now(datetime.UTC) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt