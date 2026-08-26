#-------------------------------------------------------------
# Agents with RuleBased Supervisor
#-------------------------------------------------------------

from typing import TypedDict
from langgraph.graph import START, END, StateGraph

#-------------------------------------------------------------
# Research Agent
#-------------------------------------------------------------
class InputResearchAgent(TypedDict):
    topic : str

class OutputReseachAgent(TypedDict):
    research : str

class ResearchAgent(TypedDict):
    topic    : str
    research : str

def research(state:ResearchAgent):
    topic = state["topic"]
    return {
        "research" : f"The reseach about {topic}"
    }

builder = StateGraph(
    state_schema   =ResearchAgent,
    input_schema  =InputResearchAgent,
    output_schema =OutputReseachAgent
)

builder.add_node("research", research)

builder.add_edge(START, "research")
builder.add_edge("research", END)

research_agent = builder.compile()
#-------------------------------------------------------------
# Writer Agent
#-------------------------------------------------------------
class InputWriterAgent(TypedDict):
    research : str

class OutputWriterAgent(TypedDict):
    article : str

class WriterAgent(TypedDict):
    research : str
    article  : str

def write(state: WriterAgent):
    research = state["research"]
    return {
        "article" : f"The reseach about {research}"
    }

builder = StateGraph(
    state_schema  =WriterAgent,
    input_schema  =InputWriterAgent,
    output_schema =OutputWriterAgent
)

builder.add_node("write", write)

builder.add_edge(START, "write")
builder.add_edge("write", END)

write_agent = builder.compile()

#-------------------------------------------------------------
# Main Graph
#-------------------------------------------------------------
class State(TypedDict):
    topic    : str
    research : str
    article  : str

def supervisor(state:State):
    topic = state["topic"]
    research = state.get("research", None)
    article = state.get("article", None)

    if not research:
        return "research"
    if not article:
        return "write"

builder = StateGraph(State)

builder.add_node("research", research_agent)
builder.add_node("write", write_agent)

builder.add_conditional_edges(
    START, supervisor, {
        "research" : "research",
        "write"    : "write"
    }
)

builder.add_conditional_edges(
    "research", supervisor, {
        "research" : "research",
        "write"    : "write"
    }
)

builder.add_edge("write", END)

graph = builder.compile()

result = graph.invoke(
    {
        "topic" : "LangGraph"
    }
)
print(result)
