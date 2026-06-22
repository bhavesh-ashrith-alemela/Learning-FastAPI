from fastapi import FastAPI, status, HTTPException, Request, Depends, Header
import sqlite3
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import time
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session

app = FastAPI()

#con = sqlite3.connect("test.db", check_same_thread=False)

#cursor = con.cursor()

#cursor.execute("""
#CREATE TABLE IF NOT EXISTS todos(
#        id INTEGER PRIMARY KEY,
#       title TEXT,
#       completed TEXT
#       )
#""")

#con.commit()

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread":False}
)

sessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    completed = Column(String)

Base.metadata.create_all(bind=engine)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.middleware("http")
async def log_middleware(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time()-start_time

    print(f"path:{request.url.path} | Time:{process_time}")

    return response

def verify_token(token: str = Header(None)):
    if token != "mysecrettoken":
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )
    return {
        "user": "Authorized user"
    }

def common_logic():
    return {
        "message": "common logic executed"
    }
 
def get_current_user():
    return {
        "user": "Bhavesh"
    }

class UserNotFoundException(Exception):
    def __init__(self, name:str):
         self.name=name

class User(BaseModel):
    name: str
    age: int

@app.exception_handler(UserNotFoundException)
def user_not_found(request:Request, exc:UserNotFoundException):
    return JSONResponse(
        status_code=404,
        content={
            "status": "error",
            "message": f"User {exc.name} not found"
        }
    )

#Home Route
@app.get("/")
def home(db: Session = Depends(get_db)):

    return {"message": "Welcome to the FastAPI, DB Connected fine"}

#About Route
@app.get("/about")
def about():
    return {"message": "This is an about page."}

#Query Parameters
@app.get("/users")
def get_users(name: str = None):
    return {"name": name}

@app.get("/items")
def get_items(name: str = None, price: int=0):
    return {"name": name,"price": price}

@app.post("/create_user")
def create_user(user: User):
    return {"message": "User created successfully", "user": user}

@app.get("/user")
def get_user():
    return {
        "status": "Success",
        "message": "User Fetched",
        "data": {
            "name": "bhavesh",
            "age": 21
        }
    }

@app.get("/users/{user_id}")
def get_users(user_id: int):
    if user_id != 1:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return {
        "id": 1,
        "name": "bhavesh"
    }

@app.get("/clients/{name}")
def get_user(name:str):
    if name != "bhavesh":
        raise UserNotFoundException(name)
    return {
        "name": name
    }

@app.get("/client/{user_id}")
def get_user(user_id: int):
    if user_id != 1:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return {
        "id": 1,
        "name": "bhavesh"
    }

@app.get("/home")
def home(data= Depends(common_logic)):
    return data

@app.get("/profile")
def profile(user = Depends(get_current_user)):
    return user

@app.get("/dashboard")
def dashboard(user = Depends(get_current_user)):
    return user

@app.get("/secure")
def secure(user = Depends(verify_token)):
    return {
        "message": "secure data accessed",
        "user": user
    }

@app.middleware("http")
async def my_middlewarwe(request: Request,call_next):
    print("Request Received")

    response = await call_next(request)

    print("Request sent")

    return response

@app.get("/data")
def data():
    return {
        "message": "SQLite connected fine"
    }