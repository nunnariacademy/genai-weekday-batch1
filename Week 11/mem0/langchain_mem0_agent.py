"""Simple LangChain travel agent with Mem0 memory.

Based on https://docs.mem0.ai/integrations/langchain
"""
from typing import List, Dict

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from mem0 import MemoryClient

load_dotenv()  # needs OPENAI_API_KEY and MEM0_API_KEY

llm = ChatOpenAI(model="gpt-5-nano")
mem0 = MemoryClient()

prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content=(
        "You are a helpful travel agent AI. Use the provided context to personalize "
        "your responses and remember user preferences and past interactions. "
        "Provide travel recommendations, itinerary suggestions, and answer questions "
        "about destinations."
    )),
    MessagesPlaceholder(variable_name="context"),
    ("human", "{input}"),
])


def retrieve_context(query: str, user_id: str) -> List[Dict]:
    """Search Mem0 for memories relevant to the query."""
    try:
        memories = mem0.search(query, filters={"user_id": user_id})
        serialized = " ".join(m["memory"] for m in memories["results"])
        return [{"role": "system", "content": f"Relevant information: {serialized}"}]
    except Exception as e:
        print(f"Error retrieving memories: {e}")
        return []


def generate_response(user_input: str, context: List[Dict]) -> str:
    chain = prompt | llm
    return chain.invoke({"context": context, "input": user_input}).content


def save_interaction(user_id: str, user_input: str, assistant_response: str):
    try:
        mem0.add(
            [
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": assistant_response},
            ],
            user_id=user_id,
        )
    except Exception as e:
        print(f"Error saving interaction: {e}")


def chat_turn(user_input: str, user_id: str) -> str:
    context = retrieve_context(user_input, user_id)
    response = generate_response(user_input, context)
    save_interaction(user_id, user_input, response)
    return response


if __name__ == "__main__":
    print("Welcome to your personal Travel Agent Planner! (type 'quit' to exit)")
    user_id = "alice"
    while True:
        user_input = input("You: ")
        if user_input.lower() in ("quit", "exit", "bye"):
            print("Travel Agent: Thank you for using our service. Have a great trip!")
            break
        print(f"Travel Agent: {chat_turn(user_input, user_id)}")
