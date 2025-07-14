from mcp.server.fastmcp import FastMCP
from typing import List
from uuid import uuid4
from datetime import datetime

# Initialize the MCP server with the name "TodoMCP"
mcp = FastMCP("TodoMCP")

# In-memory dictionary to store todo items.
# Format: {todo_id: {"title": str, "completed": bool, "created_at": str}}
todos = {}


# TOOL: Add a new to-do item
@mcp.tool()
def add_todo(title: str) -> str:
    """Add a new to-do item"""
    # Generate a unique ID for the todo
    todo_id = str(uuid4())
    # Save the todo with default 'completed' = False
    todos[todo_id] = {
        "title": title,
        "completed": False,
        "created_at": datetime.utcnow().isoformat()
    }
    return f"Todo '{title}' added with ID {todo_id}"


# TOOL: Mark an existing to-do item as completed
@mcp.tool()
def complete_todo(todo_id: str) -> str:
    """Mark a todo as completed"""
    todo = todos.get(todo_id)
    if not todo:
        return "Todo not found."
    if todo["completed"]:
        return "Todo already completed."

    # Update the completed flag
    todo["completed"] = True
    return f"Todo '{todo['title']}' marked as completed."


# TOOL: Delete a to-do item by ID
@mcp.tool()
def delete_todo(todo_id: str) -> str:
    """Delete a todo"""
    if todo_id in todos:
        title = todos[todo_id]["title"]
        # Remove the todo from the dictionary
        del todos[todo_id]
        return f"Todo '{title}' deleted."
    return "Todo not found."


# RESOURCE: Return a list of all to-do items
@mcp.resource("todos://all")
def list_todos() -> List[dict]:
    """List all todos"""
    # Convert internal dict format into a list of todos with IDs
    return [{"id": todo_id, **info} for todo_id, info in todos.items()]


# RESOURCE: Return details of a single to-do item by ID
@mcp.resource("todo://{todo_id}")
def get_todo(todo_id: str) -> dict:
    """Get a specific todo item"""
    todo = todos.get(todo_id)
    if not todo:
        return {"error": "Todo not found"}
    return {"id": todo_id, **todo}


# RESOURCE: Return a simple greeting message (optional/fun)
@mcp.resource("greeting://{name}")
def greet(name: str) -> str:
    """Greet a user with their name"""
    return f"Hello, {name}! Welcome to your todo manager."


# Entry point to run the MCP server
if __name__ == "__main__":
    mcp.run()
