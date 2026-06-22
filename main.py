from fastapi import FastAPI, status, HTTPException, Request, Depends, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

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
def home():
    return {"message": "Welcome to the FastAPI"}

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