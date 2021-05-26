from fastapi import FastAPI, Depends
from enum import Enum
from pydantic import BaseModel
from typing import Optional, List
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import json
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session


#Database
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Cat(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    abbr = Column(String)


class DBCategory(BaseModel):
    id: int
    name: str
    abbr: str
    
    class Config:
        orm_mode = True


Base.metadata.create_all(bind=engine)



# Pydantic
class Category(str, Enum):
    CatA = "a"
    CatB = "b"

class UserForm(BaseModel):
    categories: Optional[Category]


class UserFormDB(BaseModel):
    categories: Optional[DBCategory]



# FASTAPI

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/categories", response_model=List[DBCategory])
async def get(db: Session = Depends(get_db)):
    return db.query(Cat).all()

@app.get("/schema")
async def get():
    content = json.loads(UserForm.schema_json())
    return JSONResponse(content=content)

@app.get("/schema2")
async def get():
    content = json.loads(UserFormDB.schema_json())
    return JSONResponse(content=content)


app.mount("/", StaticFiles(directory="static"), name="static")
