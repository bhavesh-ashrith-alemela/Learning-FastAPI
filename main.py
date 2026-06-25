from fastapi import FastAPI, status, HTTPException, Request, Depends, Header, UploadFile, File
import sqlite3
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import time
import asyncio
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from fastapi.staticfiles import StaticFiles
import os
import shutil
from fastapi.middleware.cors import CORSMiddleware
# from dotenv import load_dotenv
from config import settings
import requests


app = FastAPI()

# load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
DB_URL = os.getenv("DB_URL")
origins = settings.origins

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"] 
)

#JWT Config

#Password hashing setup
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

#Oauth Setup
oauth2_schema = OAuth2PasswordBearer(tokenUrl="login")

#Dummy user DB
fake_user_db = {
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("1234")
    }
}

#Hash password
def hash_password(password: str):
    return pwd_context.hash(password)

#verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

#Create Token
def create_token(data: dict):
    to_encode = data.copy()
    expiry = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRY_MINUTES)
    to_encode.update({
        "exp": expiry
    })
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

#Login API token generator 
# @app.post("/login")
# def login(user_name: str, password: str):
#     if user_name != "admin" or password != "1234":
#         raise HTTPException(
#             status_code=401,
#             detail="Invalid User name & Password"
#         )
#     token = create_token({
#         "sub": user_name
#     })
#     return {
#         "access_token": token,
#         "token_type": "bearer"
#     }

#Login API OAuth
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_user_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=400,
            detail="Invalid username or password"
        )
    access_token = create_token({"sub":form_data.username})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

#Token verify
# def verify_token(authorization: str = Header(None), token: str = Header(None)):
#     if authorization is None and token is None:
#         raise HTTPException(
#             status_code=401,
#             detail="Authorization header missing"
#         )

#     if authorization is not None:
#         scheme, _, token_value = authorization.partition(" ")
#         if scheme.lower() != "bearer" or not token_value:
#             raise HTTPException(
#                 status_code=401,
#                 detail="Invalid authorization scheme"
#             )
#     else:
#         token_value = token

#     try:
#         payload = jwt.decode(token_value, SECRET_KEY, algorithms=[ALGORITH])
#         return payload
#     except Exception:
#         raise HTTPException(
#             status_code=401,
#             detail="Invalid or expired Token"
#         )

def verify_token(token:str = Depends(oauth2_schema)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username:str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )
        return username
    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

#protected route
# @app.get("/security")
# def secure_data(user = Depends(verify_token)):
#     return {
#         "message": "Secure data accessed",
#         "user": user
#     }

@app.get("/protected")
def protected_route(username:str = Depends(verify_token)):
    return {
        "message": f"Hello {username}, you have access to this protected route!",
        "user": username
    }

#Step-1 ensure upload folder exists
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

#Step-2 Static file stepup
#Url : http://127.0.0.1:8080/files/<filename>
app.mount("/files", StaticFiles(directory=UPLOAD_DIR), name="files")

#Step-3 upload file api
@app.post("/upload")
def upload_file(file: UploadFile = File(...)):
    filename = file.filename
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="File not selected"
        )
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

        return {
            "message": "File uploaded successfully",
            "fileName": filename,
            "file_url": f"http://127.0.0.1:8000/files/{filename}"
        }
    
#step-4 get file url api
@app.get("/files/{filename}")
def  get_file(filename:str):
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return {
        "file url": f"http://127.0.0.1:8000/files/{filename}"
    }

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

#DataBase URL
# DATABASE_URL = "sqlite:///./test.db"

#Engine Create (DB connection)
engine = create_engine(
    DB_URL,
    connect_args={"check_same_thread":False}
)

#Session for DB Operations
sessionLocal = sessionmaker(bind=engine)

#BaseModel for DB
Base = declarative_base()

#Table (also a Model)
class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    completed = Column(String)

#Table Created 
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

@app.get("/posts")
def get_posts():
    url = "https://jsonplaceholder.typicode.com/posts"
    response = requests.get(url)
    return response.json()

@app.get("/posts/{post_id}")
def get_posts_id(post_id:int):
    url = f"https://jsonplaceholder.typicode.com/posts/{post_id}"
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(
            status_code=404,
            detail="Page not found"
        )
    return response.json()


#Home Route
@app.get("/")
def home():
    return {"message": "Welcome to the FastAPI, DB Connected fine, File uploaded api running"}

#Create API
@app.post("/todos")
def create_todo(title:str, db:Session = Depends(get_db)):
    todo = Todo(title=title, completed="False")
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return {
        "message": "Todo created",
        "data": {
            "id": todo.id,
            "title": todo.title,
            "completed": todo.completed
        }
    }

#Read all data
@app.get("/todos")
def get_todos(db:Session = Depends(get_db)):
    todos = db.query(Todo).all()
    return {
        "Total": len(todos),
        "data": [
            {"id": todo.id, "title": todo.title, "completed": todo.completed}
            for todo in todos
        ]
    }

#Read data by Id
@app.get("/todos/{todo_id}")
def get_todo(todo_id:int, db:Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo :
        raise HTTPException(
            status_code=404,
            detail="Todo not found"
        )
    return {
        "message": "Found Todo",
        "data": {
            "id": todo.id,
            "title": todo.title,
            "completed": todo.completed
        }
    }

#Update data by id
@app.put("/todos/{todo_id}")
def put_todo(todo_id:int, title:str, db:Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo :
        raise HTTPException(
            status_code=404,
            detail="Todo not found"
        )
    todo.title = title
    db.commit()
    db.refresh(todo)
    return {
        "message": "Todo updated",
        "data": {
            "id": todo.id,
            "title": todo.title,
            "completed": todo.completed
        }
    }

#Delete data
@app.delete("/todos/{todo_id}")
def del_todo(todo_id:int, db:Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo :
        raise HTTPException(
            status_code=404,
            detail="Todo not found"
        )
    db.delete(todo)
    db.commit()
    return {
        "message": "Todo deleted"
    }

#Query Parameters
@app.get("/users")
def get_users_list(name: str = None):
    return {"name": name}

@app.get("/items")
def get_items(name: str = None, price: int=0):
    return {"name": name,"price": price}

@app.post("/create_user")
def create_user(user: User):
    return {"message": "User created successfully", "user": user}

@app.get("/user")
def get_user_single():
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
def get_client_by_name(name:str):
    if name != "bhavesh":
        raise UserNotFoundException(name)
    return {
        "name": name
    }

@app.get("/client/{user_id}")
def get_client_by_id(user_id: int):
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
def home_with_data(data= Depends(common_logic)):
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

#Async and Await
@app.get("/abc")
async def home():
    await asyncio.sleep(3)
    return {
        "message": "Async API"
    }

@app.get("/test")
def home():
    return {
        "message": "Hello Bhavesh"
    }

@app.get("/add")
def add(a:int, b:int):
    return {
        "return": a+b
    }