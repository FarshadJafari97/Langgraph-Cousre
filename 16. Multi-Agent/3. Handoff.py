from typing import TypedDict
from langgraph.graph import START, END, StateGraph
from langgraph.types import Command

#-------------------------------------------------------------
# Research Agent
#-------------------------------------------------------------
class InputResearchAgent(TypedDict):
    topic : str

class OutputResearchAgent(TypedDict):
    research : str

class ResearchAgent(TypedDict):
    topic    : str
    research : str

def research(state:ResearchAgent):
    topic = state["topic"]
    return Command(
        update= {"research" : f"The research about {topic}"},
        goto="write",
        graph= Command.PARENT
    )

builder = StateGraph(
    state_schema   =ResearchAgent,
    input_schema  =InputResearchAgent,
    output_schema =OutputResearchAgent
)

builder.add_node("research", research)

builder.add_edge(START, "research")

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
        "article" : f"The research about {research}"
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


builder = StateGraph(State)

builder.add_node("research", research_agent)
builder.add_node("write", write_agent)

builder.add_edge(START, "research")
builder.add_edge("write", END)

graph = builder.compile()

result = graph.invoke(
    {
        "topic" : "LangGraph"
    }
)
print(result)
