#------------------------------------------------------------
#                    Main Supervisor
#                          │
#             ┌────────────┴────────────┐
#             ↓                         ↓
#        Research Team             Writing Agent
#             │
#       ┌─────┴─────┐
#       ↓           ↓
#   Search Agent  Analyst Agent
#------------------------------------------------------------

#------------------------------------------------------------
# Search Agent
#------------------------------------------------------------
from typing import TypedDict
from langgraph.graph import StateGraph, END, START

class SearchState(TypedDict):
    topic         : str
    search_result : str

class InputSearch(TypedDict):
    topic : str

class OutputSearch(TypedDict):
    search_result : str

def searching(state:SearchState):
    topic  = state['topic']
    result = f'''
    These are result for topic : {topic}
    reslut 1 : abcs
    result 2 : amcn
    '''
    return {
        "search_result" : result
    }

builder  = StateGraph(
    state_schema  = SearchState,
    input_schema  = InputSearch,
    output_schema = OutputSearch
)

builder.add_node("search", searching)

builder.add_edge(START, "search")
builder.add_edge("search" , END)

search_agent = builder.compile()

#------------------------------------------------------------
# Analysis Agent
#------------------------------------------------------------
from typing import TypedDict
from langgraph.graph import StateGraph, END, START

class AnalysisState(TypedDict):
    topic             : str
    search_result     : str
    analysis_approval : str
    
class InputAnalysis(TypedDict):
    topic             : str
    search_result     : str

class OutputAnalysis(TypedDict):
    analysis_approval : str

def analysing(state:SearchState):
    topic  = state['topic']
    result = f'''
    These are result for topic : {topic}
    reslut 1 : abcs
    result 2 : amcn
    '''
    return {
        "analysis_approval" : "ok"
    }
builder  = StateGraph(
    state_schema  = AnalysisState,
    input_schema  = InputAnalysis,
    output_schema = OutputAnalysis
)

builder.add_node("analyse", analysing)

builder.add_edge(START, "analyse")
builder.add_edge("analyse" , END)

analyse_agent = builder.compile()

#------------------------------------------------------------
# Research Team
#------------------------------------------------------------
from typing import TypedDict
from langgraph.graph import StateGraph, END, START

class ResearchState(TypedDict):
    topic             : str
    search_result     : str
    analysis_approval : str

class InputResearch(TypedDict):
    topic             : str

class OutputResearch(TypedDict):
    search_result     : str

def start(state:ResearchState):
    return {}

def managing(state: ResearchState):
    search_result = state.get("search_result" , None)
    analysis_approval = state.get("analysis_approval" ,None)

    if search_result is None:
        return "search"
    if search_result is not None and analysis_approval is None:
        return "analyse"
    if search_result is not None and analysis_approval is not None:
        return "end"

builder = StateGraph(
    state_schema=ResearchState,
    input_schema=InputResearch,
    output_schema=OutputResearch
)

builder.add_node("start" , start)
builder.add_node("manage", managing)
builder.add_node("search" , search_agent)
builder.add_node("analyse" , analyse_agent)

builder.add_edge(START, "start")
builder.add_conditional_edges(
    "start",
    managing,
    {
        "search"  : "search",
        "analyse" : "analyse",
        "end"     : END
    }
)
builder.add_edge("search" , "start")
builder.add_edge("analyse" , "start")

research_team = builder.compile()

#------------------------------------------------------------
# Writing Team
#------------------------------------------------------------
from typing import TypedDict
from langgraph.graph import StateGraph, END, START

class WritingState(TypedDict):
    topic             : str
    search_result     : str
    report            : str

class InputWriting(TypedDict):
    topic             : str
    search_result     : str

class OutputWriting(TypedDict):
    report            : str

def writing(state: WritingState):
    topic = state["topic"]
    result = state["search_result"]
    report = f'''
    This is a writing about topic {topic} and based on result: {result} 
    '''
    return {"report" : report}

builder = StateGraph(
    state_schema=WritingState,
    input_schema=InputWriting,
    output_schema=OutputWriting
)

builder.add_node("write" , writing)

builder.add_edge(START  , 'write')
builder.add_edge('write', END)

writing_agent = builder.compile()

#------------------------------------------------------------
# Main Orchetrator
#------------------------------------------------------------
from typing import TypedDict
from langgraph.graph import StateGraph, END, START

class MainState(TypedDict):
    topic             : str
    search_result     : str
    report            : str

def start(state:MainState):
    return {}

def managing(state: MainState):
    search_result = state.get("search_result" , None)
    report        = state.get("report" ,None)

    if search_result is None:
        return "search"
    if search_result is not None and report is None:
        return "writing"
    if search_result is not None and report is not None:
        return "end"

builder  = StateGraph(MainState)

builder.add_node("start" , start)
builder.add_node("manage", managing)
builder.add_node("search"  , research_team)
builder.add_node("writing" , writing_agent)

builder.add_edge(START, "start")
builder.add_conditional_edges(
    "start",
    managing,
    {
        "search"  : "search",
        "writing" : "writing",
        "end"     : END
    }
)
builder.add_edge("search" , "start")
builder.add_edge("writing" , "start")

main_agent = builder.compile()

result = main_agent.invoke({"topic" : "Rain"})

print(result)