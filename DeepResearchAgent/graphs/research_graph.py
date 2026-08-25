from typing import TypedDict, Annotated
import operator
from langchain_openai import ChatOpenAI
from langgraph.types import Send
from langgraph.graph import StateGraph, END, START
from graphs.search_graph import search_graph

class ResearchGraph(TypedDict):
    topic          : str
    aspect         : str
    keywords       : list[str]
    search_results : Annotated[list[str], operator.add]
    report         : list[str] 

class Keywords(TypedDict):
    keywords: list[str]
  

llm = ChatOpenAI(
    model="auto",
    base_url= "http://127.0.0.1:31415/v1",
    api_key="freellmapi-704878672ffd732da01727053c869683948f26decc0f8713"
)

llm_structured = llm.with_structured_output(Keywords)

def define_keywords(state: ResearchGraph):
    topic  = state["topic"]
    aspect = state["aspect"]
    prompt = f"""
    You are a web research query generator.
    Your task is to generate up to 2 highly relevant search queries
    for researching the given topic and aspect.
    IMPORTANT RULES:
    - All search queries MUST be written in English.
    - Do NOT generate Persian, Arabic, or mixed-language queries.
    - Use natural search-engine-friendly English.
    - Queries should target reliable and informative sources.
    - Avoid vague or overly broad queries.
    - Focus specifically on the given aspect.
    Topic:
    {topic}
    Aspect:
    {aspect}
    """
    result = llm_structured.invoke(prompt)

    return {
        "keywords" : result["keywords"]
    }

def creating_worker(state: ResearchGraph):
    return [
        Send(
            "search",
            {"keyword" : keyword}
        ) for keyword in state["keywords"]
    ]

def creating_report(state: ResearchGraph):
    search_result = state["search_results"]
    text = []
    for result in search_result:
        text.append(result)
    agg_text ="\n\n".join(text)

    prompt = f"""
    You are a research analyst.
    You are given multiple English web sources collected for a specific
    research topic and aspect.
    Your task is to analyze and synthesize the information from these
    sources into a coherent research summary.
    IMPORTANT RULES:
    - Write the entire response in English.
    - Use ONLY information supported by the provided sources.
    - Do not invent facts, statistics, studies, or claims.
    - Identify the most important findings.
    - Combine overlapping information instead of repeating it.
    - Highlight important evidence, facts, trends, and conclusions.
    - If sources disagree, explicitly mention the disagreement.
    - Ignore irrelevant information.
    - Do not discuss the research process.
    - Do not write a final report for the user.
    - This is an intermediate research synthesis that will be used by
    another model to create the final report.
    Research sources:
    {agg_text}
    """
    report = llm.invoke(prompt)

    return {
        "report" : [report.content]
    }

builder = StateGraph(ResearchGraph)

builder.add_node("define" , define_keywords)
builder.add_node("search" , search_graph)
builder.add_node("report" , creating_report)

builder.add_edge(START, "define")
builder.add_conditional_edges(
    "define",
    creating_worker,
    ["search"]
)
builder.add_edge("search", "report")
builder.add_edge("report" , END)

research_graph = builder.compile()