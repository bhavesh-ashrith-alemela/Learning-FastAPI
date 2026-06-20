from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

todos = []

class Todo(BaseModel):
    id : int
    title : str
    completed : bool


@app.post("/todos")
def create_todo(todo: Todo):
    todos.append(todo)
    return {"message": "Todo added", "data": todo}

@app.get("/todos")
def  get_todos():
    return {"data": todos}

@app.get("/todos/{todo_id}")
def get_todo(todo_id: int):
    for todo in todos:
        if todo.id == todo_id:
            return {"data": todo}
        return {"error": "Todo not found"}
    