from langgraph.graph import StateGraph, END, START
from langgraph.types import Send
from typing import TypedDict, Annotated
import operator

class State(TypedDict):
    topic: str
    sections: list[str]
    result: Annotated[list[str], operator.add]
    final_report: str

class WorkerState(TypedDict):
    section : str

def section_define(state:State):
    sections = [
        "Historical Background",
        "Current Situation",
        "Future Outlook"
    ]
    return {"sections": sections}

def worker_creator(state:State):
    sections = state['sections']
    return(
        [Send(
            "worker",
            {"section" :section}
        ) for section in sections
        ]
    )

def worker(state:WorkerState):
    section = state["section"]
    result = f"Research result for {section}"
    return {"result" : [result]}

def aggregation(state:State):
    section_length = len(state["sections"])
    result_length  = len(state["result"])
    if section_length == result_length:
        return "synthesizer"
    else:
        return "__end__"

def synthesizer(state:State):
    final_report = "\n\n".join(state["result"])
    return {"final_report" : final_report}

builder = StateGraph(State)

builder.add_node("sections", section_define)
builder.add_node("worker_creation",worker_creator)
builder.add_node("worker",worker)
builder.add_node("aggregation",aggregation)
builder.add_node("synthesizer" , synthesizer)

builder.add_edge(START, "sections")
builder.add_conditional_edges(
    "sections",
    worker_creator,
    ["worker"]
)
builder.add_conditional_edges(
    "worker",
    aggregation,
    {
        "synthesizer" : "synthesizer",
        "__end__"     : "__end__"
    }
)
builder.add_edge("synthesizer", END)

graph = builder.compile()

'''
if __name__ == "__main__":
    result = graph.invoke({"topic":"Mobile on Tech"})
    print(result)
'''


from langgraph.graph import StateGraph, END, START
from langgraph.types import Send
from typing import TypedDict, Annotated
import operator

class State(TypedDict):
    topic: str
    sections: list[str]
    result: Annotated[list[str], operator.add]
    final_report: str

class WorkerState(TypedDict):
    section : str

def section_define(state:State):
    sections = [
        "Historical Background",
        "Current Situation",
        "Future Outlook"
    ]
    return {"sections": sections}

def worker_creator(state:State):
    sections = state['sections']
    return(
        [Send(
            "worker",
            {"section" :section}
        ) for section in sections
        ]
    )

def worker(state:WorkerState):
    section = state["section"]
    result = f"Research result for {section}"
    return {"result" : [result]}

def synthesizer(state:State):
    final_report = "\n\n".join(state["result"])
    return {"final_report" : final_report}

builder = StateGraph(State)

builder.add_node("sections", section_define)
builder.add_node("worker",worker)
builder.add_node("synthesizer" , synthesizer)

builder.add_edge(START, "sections")
builder.add_conditional_edges(
    "sections",
    worker_creator,
    ["worker"]
)
builder.add_edge("worker","synthesizer")
builder.add_edge("synthesizer", END)

graph = builder.compile()

'''
if __name__ == "__main__":
    result = graph.invoke({"topic":"Mobile on Tech"})
    print(result)
'''


from langchain_openai import ChatOpenAI
from typing import Annotated, TypedDict
import operator
from langgraph.types import Send
from langgraph.graph import StateGraph, START, END

# Defining Classes
class SectionDetails(TypedDict):
    section : str
    index   : int

class Sections(TypedDict):
    sections : list[SectionDetails]

class Analysis(TypedDict):
    content : str

class State(TypedDict):
    topic    : str
    sections : list[SectionDetails]
    results  : Annotated[list[SectionDetails],operator.add]
    final    : str

class WorkerState(TypedDict):
    topic   : str
    section : str
    index   : int

# Defining LLM
llm = ChatOpenAI(
    model= "auto",
    base_url="http://127.0.0.1:31415/v1",
    api_key="freellmapi-704878672ffd732da01727053c869683948f26decc0f8713"
    )

#Defining LLM with Structured Output
llm_for_section  = llm.with_structured_output(Sections)
llm_for_analysis = llm.with_structured_output(Analysis)

def sections_defining(state:State):
    topic = state["topic"]
    prompt = f'''
    یک موضوع به شما داده می‌شود. شما باید عمیقاً به ابعاد پنهان و آشکار آن موضوع فکر کنید و حداکثر ۵ جنبه کلیدی و غیرتکراری را استخراج کنید که برای نوشتن یک مقاله جامع و حرفه‌ای ضروری هستند.
    دستورالعمل‌های دقیق:
    1- تنوع و جامعیت: جنبه‌ها باید از زوایای متفاوت به موضوع نگاه کنند (مثلاً تاریخی، فنی، اقتصادی، اجتماعی، اخلاقی، آینده‌نگرانه، یا روان‌شناختی).
    2- عدم هم‌پوشانی: هیچ دو جنبه‌ای نباید در محتوا با یکدیگر تداخل داشته باشند. هر کدام باید یک بُعد مستقل از موضوع را پوشش دهند.
    3. قابلیت بسط: هر جنبه باید به اندازه‌ای ظرفیت داشته باشد که بتوان حداقل یک بخش (چند پاراگراف) از مقاله را به آن اختصاص داد.
    4. تعداد: دقیقاً بین ۳ تا ۵ جنبه انتخاب کن. اگر موضوع خیلی خاص و محدود است، همان ۳ جنبه را بده، اما به هیچ وجه از عدد ۵ تجاوز نکن.
    5. ترتیب و ایندکس‌گذاری: جنبه‌های استخراج‌شده را به ترتیب منطقی و مقاله‌وار (مثلاً از کلی به جزئی، از گذشته به آینده، یا بر اساس اهمیت) مرتب کن. به هر جنبه یک شماره ایندکس اختصاص بده که از ۱ شروع می‌شود و به ترتیب تا تعداد کل جنبه‌ها ادامه می‌یابد. این ترتیب نشان‌دهنده توالی ارائه بخش‌ها در مقاله خواهد بود.
    موضوع:
    {topic}
    '''
    result = llm_for_section.invoke(prompt)
    return {"sections" : result["sections"]}

def creating_workers(state:State):
    workers = [
        Send(
            "worker",
            {
                "topic"   : state["topic"],
                "section" : section["section"],
                "index"   : section["index"]
            }
        ) for section in state["sections"]
    ]
    return workers

def worker(state:WorkerState):
    topic   = state["topic"]
    section = state["section"]
    index   = state["index"]
    prompt = f'''
    شما یک نویسنده ارشد و مقاله‌نویس حرفه‌ای هستید. شما قرار است یک بخش از مقاله را بنویسید. وظیفه شما این است که بر اساس یک جنبه مشخص، محتوایی عمیق، مستدل و روان تولید کنید.
    - موضوع اصلی مقاله: {topic}
    - عنوان جنبه: {section}

    **دستورالعمل‌های دقیق نگارش:**
    1. **طول متن**: دقیقاً بین ۲۰۰ تا ۳۵۰ کلمه (معادل ۳ تا ۵ پاراگراف استاندارد).
    2. **ساختار ایده‌آل پاراگراف‌ها**:
    - **پاراگراف اول (معرفی)**: با یک جمله چالش‌برانگیز یا پرسشی شروع کنید که مستقیماً به شرح جنبه گره بخورد. به‌صورت کلی توضیح دهید که چرا این بُعد از موضوع اهمیت دارد.
    - **پاراگراف‌های میانی (بدنه)**: حداقل شامل ۲ پاراگراف باشد. در این بخش، استدلال‌های خود را بیاورید. از مثال‌های عینی، تشبیهات مفهومی، یا اشاره به روندهای روز (بدون نیاز به آمار دقیق و نقل قول خارجی، مگر اینکه خودتان آن را به‌صورت "بر اساس شواهد موجود..." بیان کنید) استفاده کنید.
    - **پاراگراف آخر (جمع‌بندیِ بخش)**: این پاراگراف نباید مقاله را نتیجه‌گیری کند، بلکه باید یک **جمله پل (Bridge)** باشد که نشان دهد این جنبه چگونه به درک بهتر جنبه‌های دیگر (یا خود موضوع اصلی) کمک می‌کند.
    3. **لحن**: رسمی، روان، شیوا و متقاعدکننده. از جملات کوتاه و بلند متناسب با هم استفاده کنید تا ریتم متن خوب شود. از تکرار مکرر کلمات کلیدی (به جز خود موضوع) خودداری کنید.
    خروجی فقط متن باشه و \u200e توش استفاده نشه. هیچ توضیحی در مورد دستورالعمل‌ها یا خود موضوع ندهید.
    '''
    result = llm_for_analysis.invoke(prompt)
    return {"results": [{"section": result["content"] , "index" : index}]}

def synthesizer(state: State):
    sorted_output = sorted(
        state["results"],
        key= lambda x : x["index"]
    )
    output = []
    for i in sorted_output:
        output.append(i["section"])
        result = "\n\n".join(output)
    prompt = f"""
    موضوع:{state["topic"]}
    ...
    بخش‌های تولیدشده توسط نویسندگان:
    {result}
    ...
    وظیفه:
    این بخش‌ها را به یک مقاله منسجم تبدیل کن.
    تکرارها را حذف کن.
    ترتیب منطقی ایجاد کن.
    بین بخش‌ها Transition ایجاد کن.
    """
    output = llm_for_analysis.invoke(prompt)
    return {"final" : output["content"]}

builder = StateGraph(State)

builder.add_node("sections" , sections_defining)
builder.add_node("worker", worker)
builder.add_node("synthesizer", synthesizer)

builder.add_edge(START, "sections")
builder.add_conditional_edges(
    "sections",
    creating_workers,
    ["worker"]
)
builder.add_edge("worker","synthesizer")
builder.add_edge("synthesizer", END)

graph = builder.compile()

if __name__ == "__main__":
    result = graph.invoke({"topic":"زیبایی دختری به نام مریم"})
    print(result)