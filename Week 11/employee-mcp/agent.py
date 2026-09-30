"""An agent that connects to the MCP server and lets an OpenAI model decide when to use
the server's tools, resources and prompts.

How it maps MCP -> OpenAI API:
  * MCP tools      -> passed directly as OpenAI function tools
  * MCP resources  -> exposed through one helper tool:  read_resource(uri)
  * MCP prompts    -> exposed through one helper tool:  get_prompt(name, arguments)
The catalog of available resources/prompts is written into the system prompt so the
model knows what exists.

Run:  export OPENAI_API_KEY=...   then   python agent.py
"""
import asyncio
import json
import os
import sys
from pathlib import Path

from openai import AsyncOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pydantic import AnyUrl

from dotenv import load_dotenv
load_dotenv()

MODEL = os.getenv("MODEL", "gpt-4o")
SERVER_PATH = str(Path(__file__).parent / "server.py")

# Helper tools that bridge MCP resources and prompts into the OpenAI tool-calling loop.
BRIDGE_TOOLS = [
    {
        "name": "read_resource",
        "description": "Read an MCP resource by URI (policies, performance notes, profile cards).",
        "parameters": {
            "type": "object",
            "properties": {"uri": {"type": "string", "description": "e.g. performance://guidelines"}},
            "required": ["uri"],
        },
    },
    {
        "name": "get_prompt",
        "description": "Fetch an MCP prompt template (a ready-made workflow) and then follow its instructions.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "arguments": {"type": "object", "description": "Prompt arguments as string values"},
            },
            "required": ["name"],
        },
    },
]


class EmployeeAgent:
    def __init__(self, session: ClientSession):
        self.session = session
        self.llm = AsyncOpenAI()
        self.messages: list[dict] = []
        self.tools: list[dict] = []
        self.system = ""

    async def setup(self) -> None:
        tools = (await self.session.list_tools()).tools
        resources = (await self.session.list_resources()).resources
        templates = (await self.session.list_resource_templates()).resourceTemplates
        prompts = (await self.session.list_prompts()).prompts

        mcp_tools = [
            {"name": t.name, "description": t.description or "", "parameters": t.inputSchema}
            for t in tools
        ]
        self.tools = [{"type": "function", "function": f} for f in mcp_tools + BRIDGE_TOOLS]

        res_lines = [f"- {r.uri}: {r.description}" for r in resources]
        res_lines += [f"- {t.uriTemplate}: {t.description}" for t in templates]
        prompt_lines = []
        for p in prompts:
            args = ", ".join(a.name for a in (p.arguments or [])) or "no arguments"
            prompt_lines.append(f"- {p.name}({args}): {p.description}")

        self.system = (
            "You are an HR assistant for a company. Answer using real data, never guess.\n"
            "- Use the database tools for facts (employees, salaries, projects).\n"
            "- Use read_resource for policy and written performance context.\n"
            "- If the user asks for a review, analysis or briefing that matches a prompt below, "
            "call get_prompt and follow the returned instructions.\n\n"
            "Available resources:\n" + "\n".join(res_lines) +
            "\n\nAvailable prompts:\n" + "\n".join(prompt_lines) +
            "\n\nAmounts are annual salaries in INR."
        )
        self.messages = [{"role": "system", "content": self.system}]
        self.catalog = {
            "tools": [t.name for t in tools],
            "resources": [r.uri.unicode_string() if hasattr(r.uri, "unicode_string") else str(r.uri) for r in resources]
                         + [t.uriTemplate for t in templates],
            "prompts": [p.name for p in prompts],
        }

    async def dispatch(self, name: str, args: dict) -> tuple[str, bool]:
        """Route one tool call from the model to the MCP server. Returns (text, is_error)."""
        try:
            if name == "read_resource":
                result = await self.session.read_resource(AnyUrl(args["uri"]))
                return "\n".join(c.text for c in result.contents if hasattr(c, "text")), False
            if name == "get_prompt":
                result = await self.session.get_prompt(args["name"], args.get("arguments") or {})
                return "\n".join(m.content.text for m in result.messages if m.content.type == "text"), False
            result = await self.session.call_tool(name, args)
            text = "\n".join(c.text for c in result.content if c.type == "text")
            return text, bool(result.isError)
        except Exception as exc:  # let the model see the error and recover
            return f"Error: {exc}", True

    async def chat(self, user_text: str) -> str:
        self.messages.append({"role": "user", "content": user_text})
        while True:
            resp = await self.llm.chat.completions.create(
                model=MODEL, messages=self.messages, tools=self.tools,
            )
            msg = resp.choices[0].message
            self.messages.append(msg.model_dump(exclude_none=True))
            if not msg.tool_calls:
                return msg.content or ""

            for call in msg.tool_calls:
                args = json.loads(call.function.arguments or "{}")
                print(f"  [tool] {call.function.name} {json.dumps(args)}")
                text, _is_error = await self.dispatch(call.function.name, args)
                self.messages.append({
                    "role": "tool", "tool_call_id": call.id, "content": text,
                })


async def main() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        sys.exit("Set OPENAI_API_KEY first.")

    # The client launches the server as a subprocess and talks to it over stdio.
    params = StdioServerParameters(command=sys.executable, args=[SERVER_PATH], env=dict(os.environ))
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            agent = EmployeeAgent(session)
            await agent.setup()

            print("Employee agent ready. Commands: /tools /resources /prompts /quit")
            while True:
                user = (await asyncio.to_thread(input, "\nyou> ")).strip()
                if not user:
                    continue
                if user == "/quit":
                    break
                if user in ("/tools", "/resources", "/prompts"):
                    print("\n".join(agent.catalog[user[1:]]))
                    continue
                print("\n" + await agent.chat(user))


if __name__ == "__main__":
    asyncio.run(main())
