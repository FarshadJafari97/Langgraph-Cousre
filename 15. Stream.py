#------------------------------------------------------------
# Values, Updates, Debug Mode
#------------------------------------------------------------
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    text: str
    cleaned: str
    result: str

def clean_text(state: State):
    cleaned = state["text"].strip().lower()

    return {"cleaned": cleaned}

def summarize_text(state: State):
    result = f"Processed text: {state['cleaned']}"

    return {"result": result}


builder = StateGraph(State)

builder.add_node("clean", clean_text)
builder.add_node("summarize",summarize_text)

builder.add_edge(START, "clean")
builder.add_edge("clean", "summarize")
builder.add_edge("summarize",END)

graph = builder.compile()

for chunk in graph.stream(
    {
        "text": "   Hello LangGraph   "
    },
    stream_mode="values", # or "updates" or "debug"
):
    print(chunk)

#------------------------------------------------------------
# Message Mode
#------------------------------------------------------------
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model = "auto",
    base_url= "http://127.0.0.1:31415/v1",
    api_key= "freellmapi-704878672ffd732da01727053c869683948f26decc0f8713"
)

class State(TypedDict):
    text: str
    result: str

def message_mode(state: State):
    prompt = f"Give me a long story about this: {state['text']}"
    result = llm.invoke(prompt)

    return {
        "result": result.content
    }

builder = StateGraph(State)

builder.add_node("message", message_mode)

builder.add_edge(START, "message")
builder.add_edge("message",END)

graph = builder.compile()
for msg, metadata in graph.stream(
    {
        "text": "Effect of global warming on polar bears"
    },
    stream_mode="messages",
):
    if msg:
        print(msg.content, end="" , flush=True)
