from sqlalchemy import Column, Integer, String
from database import Base


class User(Base):
    
    """
    Database model for representing users.

    Attributes:
        id (int): The primary key identifier for the user.
        name (str): The name of the user.
        password (str): The hashed password of the user.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    name = Column(String)
    password=Column(String)
