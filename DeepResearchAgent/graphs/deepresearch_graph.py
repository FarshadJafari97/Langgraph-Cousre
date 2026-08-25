from typing import TypedDict, Annotated
import operator
from langchain_openai import ChatOpenAI
from graphs.search_graph import search_graph
from graphs.research_graph import Keywords , research_graph
from langgraph.types import Send
from langgraph.graph import START, END, StateGraph

def merge_str(old: str, new: str) -> str:
    return new

class State(TypedDict):
    topic                    : Annotated[str, merge_str]
    general_initial_keywords : list[str]
    search_results           : Annotated[list[str], operator.add]
    aspects                  : list[str]
    report                   : Annotated[list[str], operator.add]
    final_report             : str

llm = ChatOpenAI(
    model    = "auto",
    base_url = "http://127.0.0.1:31415/v1",
    api_key  = "freellmapi-704878672ffd732da01727053c869683948f26decc0f8713"
)

llm_keywords_aspects = llm.with_structured_output(Keywords)

def initial_keywords(state:State):
    topic = state["topic"]
    prompt = f"""
    You are an expert web research query generator.
    Generate exactly 2 highly relevant initial search queries
    for researching the given topic.
    IMPORTANT RULES:
    - Both queries MUST be written entirely in English.
    - Do NOT use Persian, Arabic, or mixed-language text.
    - Queries must be suitable for English web search engines.
    - The two queries should approach the topic from slightly different
    perspectives.
    - Prefer specific and informative queries over generic queries.
    - Focus on finding reliable, factual, and research-oriented information.
    Topic:
    {topic}
    """
    result= llm_keywords_aspects.invoke(prompt)

    return {"general_initial_keywords" : result["keywords"]}

def creating_worker_initail_search(state: State):
    return [
        Send(
            "keywords_search",
            {
                "keyword" : keyword,
            }
        ) for keyword in state["general_initial_keywords"]
    ]

def aspects(state:State):
    topic = state["topic"]
    initial_result = "\n\n".join(state["search_results"])
    prompt = f"""
    You are an expert research planner.
    Your task is to identify exactly 2 major and complementary research
    aspects for the given topic based on the initial search results.
    IMPORTANT RULES:
    - The aspects MUST be written entirely in English.
    - Do NOT use Persian, Arabic, or mixed-language text.
    - The two aspects should cover substantially different dimensions
    of the topic.
    - Avoid overlapping aspects.
    - Each aspect must be specific enough to support a separate
    research process.
    - Prioritize important dimensions that require deeper investigation.
    - Do not simply repeat the topic.
    - Do not generate questions; generate concise research aspects.
    - Use the initial search results only as context for identifying
    important research directions.
    Topic:
    {topic}
    Initial search results:
    {initial_result}
    """
    result = llm_keywords_aspects.invoke(prompt)
    return {"aspects" : result["keywords"]}

def creating_workers_research(state:State):
    topic = state["topic"]
    return [
        Send(
            "research",
            {
                "topic" :  topic,
                "aspect":  aspect
            }
        ) for aspect in state["aspects"]
    ]

def final_result(state:State):
    topic = state["topic"]
    aspects = "--".join(state["aspects"])
    agg_text = "\n\n".join(state["report"])
    prompt = f"""
    You are an expert research writer.
    You are given the results of a multi-stage research process about
    a specific topic.
    Your task is to produce the final research report in Persian.
    IMPORTANT LANGUAGE RULE:
    - The entire final report MUST be written in Persian.
    - Do NOT write the report in English.
    - English technical terms may be included in parentheses when
    necessary for clarity.
    - Keep proper names, organization names, study names, and technical
    terms in their original English form when translating them would
    reduce accuracy.
    IMPORTANT CONTENT RULES:
    - Base the report ONLY on the provided research findings.
    - Do NOT invent facts, statistics, studies, or conclusions.
    - Synthesize the findings instead of simply copying or listing them.
    - Remove duplicate information.
    - Clearly explain the most important findings.
    - Preserve important facts, evidence, numbers, dates, and comparisons.
    - If the research findings contain conflicting claims, mention the
    disagreement rather than choosing one without evidence.
    - Distinguish established findings from uncertain or limited evidence.
    - Maintain an objective and analytical tone.
    - Do not mention that you are an AI.
    - Do not describe the internal research process.
    - Do not mention these instructions.
    REPORT STRUCTURE:
    1. عنوان
    2. مقدمه
    3. بررسی جنبه‌های اصلی موضوع
    4. مهم‌ترین یافته‌ها و شواهد
    5. تحلیل و جمع‌بندی
    6. نتیجه‌گیری
    Topic:
    {topic}
    Research aspects:
    {aspects}
    Research findings:
    {agg_text}
    """
    result = llm.invoke(prompt)

    return {"final_report" : result.content}

builder = StateGraph(State)

builder.add_node("initial_keywords", initial_keywords)
builder.add_node("keywords_search" , search_graph)
builder.add_node("aspects" , aspects)
builder.add_node("research", research_graph)
builder.add_node("final_result" , final_result)

builder.add_edge(START, "initial_keywords")
builder.add_conditional_edges(
    "initial_keywords",
    creating_worker_initail_search,
    ["keywords_search"]
)
builder.add_edge("keywords_search","aspects")
builder.add_conditional_edges(
    "aspects",
    creating_workers_research,
    ["research"]
)
builder.add_edge("research", "final_result")
builder.add_edge("final_result", END)

deepresearchgraph = builder.compile()