# basic-mcp

A minimal Model Context Protocol (MCP) server and client example in Python.

## Features
- Simple MCP server with:
  - Addition tool
  - Static and dynamic resources
  - Prompt examples
- Async client that demonstrates:
  - Listing tools and resources
  - Calling tools and prompts
  - Reading resources

## Usage

### 1. Install dependencies
You need the `mcp` package. Install it with pip if not already installed:

```bash
pip install mcp
```

### 2. Run the server

```bash
python server.py
```

### 3. Run the client (in another terminal)

```bash
python client.py
```

## File Structure
- `server.py` — MCP server implementation
- `client.py` — Example async client

## Requirements
- Python 3.8+
- `mcp` Python package

---

This is a minimal example for learning and experimentation with MCP in Python.
