from fastapi import FastAPI

app = FastAPI()

#Home Route
@app.get("/")
def home():
    return {"message": "Welcome to the FastAPI"}

#About Route
@app.get("/about")
def about():
    return {"message": "This is an about page."}

#Users Route
@app.get("/users")
def users():
    return {"users": ["Mohith","Rohit","Amit"]}