from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel

app = FastAPI()


class User(BaseModel):
    name: str
    age: int

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