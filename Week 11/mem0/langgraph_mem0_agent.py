"""Simple LangGraph customer-support agent with Mem0 memory.

Based on https://docs.mem0.ai/integrations/langgraph
"""
from typing import Annotated, TypedDict, List

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from mem0 import MemoryClient

load_dotenv()  # needs OPENAI_API_KEY and MEM0_API_KEY

llm = ChatOpenAI(model="gpt-5-nano")
mem0 = MemoryClient()


class State(TypedDict):
    messages: Annotated[List[HumanMessage | AIMessage], add_messages]
    mem0_user_id: str


def chatbot(state: State):
    messages = state["messages"]
    user_id = state["mem0_user_id"]

    try:
        memories = mem0.search(messages[-1].content, filters={"user_id": user_id})
        context = "Relevant information from previous conversations:\n"
        for memory in memories["results"]:
            context += f"- {memory['memory']}\n"

        system_message = SystemMessage(content=(
            "You are a helpful customer support assistant. Use the provided context "
            "to personalize your responses and remember user preferences and past "
            f"interactions.\n{context}"
        ))
        response = llm.invoke([system_message] + messages)

        try:
            result = mem0.add(
                [
                    {"role": "user", "content": messages[-1].content},
                    {"role": "assistant", "content": response.content},
                ],
                user_id=user_id,
            )
            print(f"[Memory saved: {len(result.get('results', []))} memories added]")
        except Exception as e:
            print(f"Error saving memory: {e}")

        return {"messages": [response]}
    except Exception as e:
        print(f"Error in chatbot: {e}")
        return {"messages": [llm.invoke(messages)]}


graph = StateGraph(State)
graph.add_node("chatbot", chatbot)
graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", END)  # the guide loops chatbot->chatbot; END stops after one reply
compiled_graph = graph.compile()


def run_conversation(user_input: str, mem0_user_id: str):
    state = {"messages": [HumanMessage(content=user_input)], "mem0_user_id": mem0_user_id}
    result = compiled_graph.invoke(state)
    print("Customer Support:", result["messages"][-1].content)


if __name__ == "__main__":
    print("Welcome to Customer Support! How can I assist you today? (type 'quit' to exit)")
    mem0_user_id = "alice"
    while True:
        user_input = input("You: ")
        if user_input.lower() in ("quit", "exit", "bye"):
            print("Customer Support: Thank you for contacting us. Have a great day!")
            break
        run_conversation(user_input, mem0_user_id)
