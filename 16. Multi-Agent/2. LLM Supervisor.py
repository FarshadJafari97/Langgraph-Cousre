#-------------------------------------------------------------
# Agents with LLM Supervisor
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
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from typing import Literal

class State(TypedDict):
    topic    : str
    research : str
    article  : str

class SupervisorAgent(BaseModel):
    direction : Literal["research" , "write", "end"]

llm = ChatOpenAI(
    model    = "auto",
    base_url = "http://127.0.0.1:31415/v1",
    api_key  = "freellmapi-704878672ffd732da01727053c869683948f26decc0f8713"  
)

supervisor_llm = llm.with_structured_output(SupervisorAgent)


def supervisor(state:State):
    research = state.get("research", "")
    article = state.get("article", "")

    prompt= f'''
    تو به عنوان یک سوپروایزر در یک گراف ببین اگه زیر تحقیق  خالی بود research رو برگردون که انجام بشه
    و اگه زیر مقاله خالی بود، article  برگردون که بره و انجام بشه.
    خالی دقیقا منظورم هیچیه، یعنی اگه یه جمله کوتاه هم بود پر در نظر بگیر
    اگه هم زیر هر دو پر بود end رو برگردون
    تحقیق :
    {research}

    مقاله:
    {article}
    '''
    result = supervisor_llm.invoke(prompt)
    return result.direction

builder = StateGraph(State)

builder.add_node("research", research_agent)
builder.add_node("write", write_agent)

builder.add_conditional_edges(
    START, 
    supervisor, 
    {
        "research" : "research",
        "write"    : "write",
        "end"      : END
    }
)

builder.add_conditional_edges(
    "research", 
    supervisor, 
    {
        "end"      : END,
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
