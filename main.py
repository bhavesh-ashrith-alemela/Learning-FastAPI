from fastapi import FastAPI, status
from pydantic import BaseModel

app = FastAPI()

class Address(BaseModel):
    city: str
    zip_code: str

class User(BaseModel):
    name: str
    age: int
    address: Address

# Home Route
@app.get("/")
def home():
    return {"message": "Welcome to the FastAPI"}

# About Route
@app.get("/about")
def about():
    return {"message": "This is an about page."}

# Defined users route
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}

# Query Parameters
@app.get("/users")
def get_users(name: str = None):
    return {"name": name}

@app.get("/items")
def get_items(name: str = None, price: int = 0):
    return {"name": name, "price": price}

# FIXED: Single, merged POST route
@app.post("/create_user", status_code=status.HTTP_201_CREATED)
def create_user(user: User):
    return {
        "message": "User created successfully", 
        "user": user
    }

@app.get("/user")
def get_user():
    return {
        "status": "Success",
        "message": "User Fetched",
        "data": {
            "name": "Mohit",
            "age": 21,
        }
    }