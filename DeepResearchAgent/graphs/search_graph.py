from typing import TypedDict
from ddgs import DDGS
import trafilatura
from langgraph.graph import StateGraph, END, START

class SearchGraph(TypedDict):
    keyword         : str
    links           : list[str]
    search_results  : list[str]

def search(state: SearchGraph):
    try:
        results = DDGS().text(
            state["keyword"],
            max_results=5
        )
        links = [r.get("href") for r in results]

        return {
            "links": links
        }

    except Exception as e:

        print(f"Search failed for: {state['keyword']}")
        print(e)

        return {
            "links": []
        }

def extraction(state:SearchGraph):
    links = state["links"]
    results = []
    for link in links:
        downloaded = trafilatura.fetch_url(link)
        if not downloaded:
            results.append("--")
        text = trafilatura.extract(downloaded)
        if text:
            results.append(text)
        else:
            results.append("--")
    return {
        "search_results" : results
    }

builder = StateGraph(SearchGraph)

builder.add_node("search", search)
builder.add_node("extract" , extraction)

builder.add_edge(START,"search")
builder.add_edge("search","extract")
builder.add_edge("extract" , END)

search_graph = builder.compile()

