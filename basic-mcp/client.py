from mcp import ClientSession
from mcp.client.sse import sse_client


async def run():
    async with sse_client(url="http://127.0.0.1:8000/sse") as streams:
        async with ClientSession(*streams) as session:
            
            await session.initialize()
            
            # List all available tools
            tools = await session.list_tools()
            print(tools)
            
            # # Call a tool
            result = await session.call_tool("add", arguments={"a": 4, "b": 5})
            print(result.content[0].text)
            
            ### List available resource
            resources = await session.list_resources()
            print("resources", resources)
            
            ### Read a resource
            content = await session.read_resource("resource://some_static_resource")
            print("content", content.contents[0].text)
            
            ### Read a resource
            content = await session.read_resource("greeting://kebede")
            print("content", content.contents[0].text)
            
            ### List available prompts
            prompts = await session.list_prompts()
            print("prompts", prompts)
            
            ### Call a prompt
            review = await session.get_prompt("review_code", arguments={"code": "print('Hello World!')"})
            print("review", review)
            
            
if __name__ == "__main__":
    import asyncio
    
    asyncio.run(run())