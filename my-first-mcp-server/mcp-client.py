#!/usr/bin/env python3
"""
Simple MCP Client for TodoMCP Server
Interacts with the mcp-server.py todo management server
"""

import asyncio
import json
import sys
from typing import Dict, Any, Optional, List
import subprocess
import signal
import os

class SimpleMCPClient:
    """Simple MCP client that communicates via stdio with the TodoMCP server"""
    
    def __init__(self, server_script: str = "mcp-server.py"):
        self.server_script = server_script
        self.process = None
        self.message_id = 0
        
    async def __aenter__(self):
        await self.start_server()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop_server()
        
    async def start_server(self):
        """Start the MCP server process"""
        try:
            self.process = await asyncio.create_subprocess_exec(
                sys.executable, self.server_script,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Initialize the MCP session
            await self.initialize()
            print("✅ Connected to TodoMCP server")
            
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            raise
            
    async def stop_server(self):
        """Stop the MCP server process"""
        if self.process:
            try:
                self.process.terminate()
                await self.process.wait()
                print("🔌 Disconnected from TodoMCP server")
            except Exception as e:
                print(f"⚠️  Error stopping server: {e}")
                
    def _get_next_id(self) -> int:
        """Generate next message ID"""
        self.message_id += 1
        return self.message_id
        
    async def send_message(self, method: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Send a JSON-RPC message to the server"""
        message = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": method,
            "params": params or {}
        }
        
        # Send message
        message_json = json.dumps(message) + "\n"
        self.process.stdin.write(message_json.encode())
        await self.process.stdin.drain()
        
        # Read response
        response_line = await self.process.stdout.readline()
        if not response_line:
            raise Exception("No response from server")
            
        response = json.loads(response_line.decode().strip())
        
        if "error" in response:
            raise Exception(f"Server error: {response['error']}")
            
        return response.get("result", {})
        
    async def initialize(self):
        """Initialize the MCP session"""
        result = await self.send_message("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "roots": {"listChanged": True},
                "sampling": {}
            },
            "clientInfo": {
                "name": "simple-todo-client",
                "version": "1.0.0"
            }
        })
        return result
        
    # Todo Management Methods
    
    async def add_todo(self, title: str) -> str:
        """Add a new todo item"""
        result = await self.send_message("tools/call", {
            "name": "add_todo",
            "arguments": {"title": title}
        })
        return result["content"][0]["text"]
        
    async def complete_todo(self, todo_id: str) -> str:
        """Mark a todo as completed"""
        result = await self.send_message("tools/call", {
            "name": "complete_todo",
            "arguments": {"todo_id": todo_id}
        })
        return result["content"][0]["text"]
        
    async def delete_todo(self, todo_id: str) -> str:
        """Delete a todo item"""
        result = await self.send_message("tools/call", {
            "name": "delete_todo",
            "arguments": {"todo_id": todo_id}
        })
        return result["content"][0]["text"]
        
    async def list_todos(self) -> List[Dict]:
        """Get all todo items"""
        result = await self.send_message("resources/read", {
            "uri": "todos://all"
        })
        return result["contents"][0]["text"]
        
    async def get_todo(self, todo_id: str) -> Dict:
        """Get a specific todo item"""
        result = await self.send_message("resources/read", {
            "uri": f"todo://{todo_id}"
        })
        return result["contents"][0]["text"]
        
    async def greet(self, name: str) -> str:
        """Get a greeting message"""
        result = await self.send_message("resources/read", {
            "uri": f"greeting://{name}"
        })
        return result["contents"][0]["text"]

class TodoCLI:
    """Command-line interface for the todo manager"""
    
    def __init__(self):
        self.client = None
        
    async def run(self):
        """Run the interactive CLI"""
        print("🚀 Starting TodoMCP Client...")
        print("Type 'help' for available commands, 'quit' to exit\n")
        
        async with SimpleMCPClient() as client:
            self.client = client
            
            while True:
                try:
                    command = input("todo> ").strip()
                    if not command:
                        continue
                        
                    if command.lower() in ['quit', 'exit', 'q']:
                        break
                        
                    await self.handle_command(command)
                    
                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    break
                except EOFError:
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
                    
    async def handle_command(self, command: str):
        """Handle user commands"""
        parts = command.split()
        cmd = parts[0].lower()
        
        if cmd == 'help':
            self.show_help()
            
        elif cmd == 'add':
            if len(parts) < 2:
                print("Usage: add <title>")
                return
            title = ' '.join(parts[1:])
            result = await self.client.add_todo(title)
            print(f"✅ {result}")
            
        elif cmd == 'list':
            todos = await self.client.list_todos()
            if not todos:
                print("📝 No todos found")
            else:
                print("\n📋 Your Todos:")
                for todo in todos:
                    status = "✅" if todo["completed"] else "⏳"
                    print(f"  {status} [{todo['id'][:8]}] {todo['title']}")
                print()
                
        elif cmd == 'complete':
            if len(parts) != 2:
                print("Usage: complete <todo_id>")
                return
            result = await self.client.complete_todo(parts[1])
            print(f"✅ {result}")
            
        elif cmd == 'delete':
            if len(parts) != 2:
                print("Usage: delete <todo_id>")
                return
            result = await self.client.delete_todo(parts[1])
            print(f"🗑️  {result}")
            
        elif cmd == 'get':
            if len(parts) != 2:
                print("Usage: get <todo_id>")
                return
            todo = await self.client.get_todo(parts[1])
            if "error" in todo:
                print(f"❌ {todo['error']}")
            else:
                status = "✅ Completed" if todo["completed"] else "⏳ Pending"
                print(f"\n📝 Todo Details:")
                print(f"   ID: {todo['id']}")
                print(f"   Title: {todo['title']}")
                print(f"   Status: {status}")
                print(f"   Created: {todo['created_at']}")
                print()
                
        elif cmd == 'greet':
            name = parts[1] if len(parts) > 1 else "User"
            greeting = await self.client.greet(name)
            print(f"👋 {greeting}")
            
        else:
            print(f"❌ Unknown command: {cmd}")
            print("Type 'help' for available commands")
            
    def show_help(self):
        """Show available commands"""
        print("""
📚 Available Commands:
  add <title>       - Add a new todo
  list             - List all todos
  complete <id>    - Mark todo as completed
  delete <id>      - Delete a todo
  get <id>         - Get todo details
  greet [name]     - Get a greeting
  help             - Show this help
  quit             - Exit the client

💡 Tips:
  - Use the first 8 characters of the ID for commands
  - Todo IDs are shown in square brackets when listing
        """)

async def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Run some test commands
        print("🧪 Running test commands...")
        async with SimpleMCPClient() as client:
            # Test adding todos
            print("Adding todos...")
            await client.add_todo("Buy groceries")
            await client.add_todo("Walk the dog")
            await client.add_todo("Finish project")
            
            # List todos
            print("\nListing todos...")
            todos = await client.list_todos()
            for todo in todos:
                print(f"  - {todo['title']} (ID: {todo['id'][:8]})")
                
            # Complete first todo
            if todos:
                first_id = todos[0]['id']
                print(f"\nCompleting todo: {first_id[:8]}")
                await client.complete_todo(first_id)
                
            # List again
            print("\nListing todos after completion...")
            todos = await client.list_todos()
            for todo in todos:
                status = "✅" if todo["completed"] else "⏳"
                print(f"  {status} {todo['title']} (ID: {todo['id'][:8]})")
                
    else:
        # Run interactive CLI
        cli = TodoCLI()
        await cli.run()

if __name__ == "__main__":
    asyncio.run(main())