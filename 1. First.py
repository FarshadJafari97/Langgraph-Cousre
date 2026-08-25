from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    input_txt:    str
    cleaned_txt:  str
    shortened_txt: str
    final_txt:    str

def cleaning_text(state: State):
    cleaned = state["input_txt"].strip().lower()
    return {"cleaned_txt": cleaned}

def shortening_text(state: State):
    shortened_text = state["cleaned_txt"][:12]
    return {"shortened_txt" : shortened_text}

def summerizing_text(state: State):
    final = (
        f"Raw Text: {state['input_txt']!r} \n"
        f"Cleaned Text: {state['cleaned_txt']!r} \n"
        f"Shortened Tetx: {state['shortened_txt']!r}"
    )
    return {"final_txt": final}

builder = StateGraph(State)

builder.add_node("Clean"  ,cleaning_text)
builder.add_node("Short",shortening_text)
builder.add_node("Final", summerizing_text)

builder.add_edge(START, "Clean")
builder.add_edge("Clean", "Short")
builder.add_edge("Short","Final")
builder.add_edge("Final", END)

graph = builder.compile()

#-----------------------------------------------------------------------
'''
if __name__ == "__main__":
    input_text = {"input_txt": "   Hi I am Farshad    "}
    result = graph.invoke(input_text)
    print(result["final_txt"])
'''
#-----------------------------------------------------------------------
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END, START

def my_reducer(old_value,new_value):
    return old_value+new_value

class State(TypedDict):
    #message: Annotated[list[str], my_reducer]
    message: list[str]

def first_node(state: State):
    return {"message":["Hi this is my first message!"]}

def second_node(state: State):
    return {"message":["This is my Second MSG!"]}

def final_node(state: State):
    print(state["message"])


graph = StateGraph(State)

graph.add_node("first", first_node)
graph.add_node("second", second_node)
graph.add_node("final", final_node)

graph.add_edge(START,"first")
graph.add_edge("first","second")
graph.add_edge("second", "final")
graph.add_edge("final",  END)

builder = graph.compile()

'''
if __name__ == "__main__":
    builder.invoke({"message": []})
'''

from langgraph.graph         import START, END, StateGraph, MessagesState
from langchain_core.messages import AIMessage, HumanMessage

class State(MessagesState):
    pass

def first(state: State):
    return{
        "messages":[HumanMessage(content="Hello, my name is Farshad.")]
    }

def second(state:State):
    return{
        "messages":[
            AIMessage(content="Nice to meet you, Farshad!")
        ]
    }
builder = StateGraph(State)

builder.add_node("first", first)
builder.add_node("second" , second)

builder.add_edge(START,"first")
builder.add_edge("first","second")
builder.add_edge("second", END)

graph = builder.compile()

'''
if __name__ == "__main__" :
    result = graph.invoke({"messages" : [HumanMessage(content="Hello")]})
    for message in result["messages"]:
        print(message.content, "\n")
'''

from langgraph.graph import END, START, StateGraph
from typing import TypedDict

class State(TypedDict):
    ticket: str
    category: str
    response: str

def classify_ticket(state:State):
    request = state["ticket"].strip().lower()
    if "payment" in request:
        return{
            "category" : "payment"
        }
    elif "error" in request or "bug" in request:
        return{
            "category" : "technical"
        }
    else:
        return{
            "category": "other"
        }
    
def payment_handler(state:State):
    return{
        "response": "Your Payment Issue Has been Recieved!"
    }

def technical_handler(state:State):
    return{
        "response": "Your Technical Issue Has been Recieved!"
    }

def other_handler(state:State):
    return{
        "response": "Your Issue Has been Recieved!"
    }

def routing(state:State):
    return state["category"]

builder = StateGraph(State)

builder.add_node("classify" , classify_ticket)
builder.add_node("technical", technical_handler)
builder.add_node("payment"  ,payment_handler )
builder.add_node("other" , other_handler)

builder.add_edge(START, "classify")
builder.add_conditional_edges(
    "classify",
    routing,
    {
        "payment"   : "payment" ,
        "technical" : "technical",
        "other"     : "other",
    }
)
builder.add_edge("other" , END)
builder.add_edge( "technical", END)
builder.add_edge("payment" , END)

graph = builder.compile()

'''
if __name__ == "__main__":
    result = graph.invoke({
        "ticket" : "The weather is too hot!"
    })
    print(result["response"])
'''

from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class State(TypedDict):
    sentence:   str
    sentiment:  str
    length :    str

def sentiment_analyzer(state:State):
    text = state["sentence"].strip().lower()
    if "happy" in text or "delight" in text:
        return{
            "sentiment" : "Positive"
        }
    elif "sad" in text or "cry" in text:
        return{
            "sentiment" : "Negative"
        } 
    else:
        return{
            "sentiment" : "Neutral"
        }

def length_analyzer(state : State):
    if len(state["sentence"]) > 20:
        return{
            "length" : "Long"
        }
    else:
        return{
            "length" : "Short"
        }

builder = StateGraph(State)

builder.add_node("sentiment", sentiment_analyzer)
builder.add_node("length" , length_analyzer)

builder.add_edge(START,"length")
builder.add_edge(START,"sentiment")
builder.add_edge("sentiment", END)
builder.add_edge("length",END)

graph = builder.compile()

'''
if __name__ == "__main__":
    result = graph.invoke(
        {
            "sentence" : "Hi I am So Happy and I think world is so beautiful."
        }
    )
    print(result)
'''


from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from typing import TypedDict

class State(TypedDict):
    sentence : str
    category : str
    response : str

def categorizing (state: State):
    text = state["sentence"]
    if "payment" in text.strip().lower():
        return Command(
            update={
                "category" : "Financial"
            },
            goto="financial_handler"
        )
    if "bug" in text.strip().lower():
        return Command(
            update={
                "category": "technical"
            },
            goto= "technical_handler"
        )
def financial_handler(state:State):
    return{
        "response": "Your Payment Issue Has been Recieved!"
    }

def technical_handler(state:State):
    return{
        "response": "Your Technical Issue Has been Recieved!"
    }

builder = StateGraph(State)

builder.add_node("category" , categorizing)
builder.add_node("financial_handler" , financial_handler)
builder.add_node("technical_handler", technical_handler)

builder.add_edge(START,"category")
builder.add_edge("financial_handler", END)
builder.add_edge("technical_handler", END)

graph = builder.compile()


from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from typing import TypedDict, Literal

class State(TypedDict):
    order    : str
    category : str
    response : str

def categorizing (state: State) -> Command[Literal["food_handler","electronics_handler","other_handler"]]:
    text = state["order"]
    if "pizza" in text.strip().lower() or "burger" in text.strip().lower():
        return Command(
            update={
                "category" : "food"
            },
            goto="food_handler"
        )
    elif "laptop" in text.strip().lower() or "phone" in text.strip().lower():
        return Command(
            update={
                "category": "electronics"
            },
            goto= "electronics_handler"
        )
    else:
        return Command(
            update={
                "category": "other"
            },
            goto="other_handler"
        )

def food_handler(state:State):
    return{
        "response": "Your food order Has been Recieved!"
    }

def electronics_handler(state:State):
    return{
        "response": "Your Electronics Order Has been Recieved!"
    }

def other_handler(state:State):
    return{
        "response": "Your Other Order Has been Recieved!"
    }

builder = StateGraph(State)

builder.add_node("category" , categorizing)
builder.add_node("food_handler" , food_handler)
builder.add_node("electronics_handler", electronics_handler)
builder.add_node("other_handler", other_handler)

builder.add_edge(START,"category")
builder.add_edge("food_handler", END)
builder.add_edge("electronics_handler", END)
builder.add_edge("other_handler", END)

graph = builder.compile()

'''
if __name__ == "__main__":
    result = graph.invoke({"order":"I need a possset"})

    print (result)
'''

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from typing import TypedDict, Annotated
import operator

class State(TypedDict):
    numbers: list[int]
    squares: Annotated[list[int], operator.add] 
    total  : int 

def map_numbers(state:State):
    number_list=[]
    for s in state["numbers"]:
        number_list.append(Send("square_worker", {"number":s}))
    return number_list
class WorkerState(TypedDict):
    number: int
    
def square_worker(state):
    number = state["number"]
    return {
        "squares" : [number*number]
    }

def summing_total(state:State):
    return{
        "total" : sum(state["squares"])
    }

builder = StateGraph(State)

builder.add_node("map"          , map_numbers)
builder.add_node("square_worker", square_worker)
builder.add_node("sum"          , summing_total)

#builder.add_edge(START, "map")
builder.add_conditional_edges(START,map_numbers,["square_worker"])
builder.add_edge("square_worker","sum")
builder.add_edge("sum", END)

graph = builder.compile()

'''
if __name__ == "__main__":
    result = graph.invoke({"numbers":[1,2,3,4,5]})

    print (result)
'''

from langgraph.graph import START, END, StateGraph
from langgraph.types import Send
from  typing import TypedDict, Annotated
import operator

class State(TypedDict):
    texts:        list[str]
    word_counts : Annotated [list[int], operator.add]
    total       : int

def map_text(state: State):
    return([
        Send("count",{"text": t}) for t in state["texts"]
    ])

def word_counter(state):
    words_count = len(state["text"].split())
    return{
        "word_counts" : [words_count]
    }

def total_sum(state: State):
    return{
        "total": sum(state["word_counts"])
    }

builder = StateGraph(State)

builder.add_node("count" , word_counter)
builder.add_node("total", total_sum)

builder.add_conditional_edges(START, map_text, ["count"])
builder.add_edge("count", "total")
builder.add_edge("total", END)

graph = builder.compile()

'''
if __name__ == "__main__":
    result = graph.invoke(
        {
            "texts":[
                "hello world",
                "langgraph is powerful",
                "agent systems are interesting"
            ]
        }
    )
    print(result)
'''

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode

@tool
def multiply(a: int , b: int) -> int:
    '''Recieve Two number and give multiplication of Those'''
    return a*b

tools = [multiply]

llm = ChatOpenAI(
    model ="auto",
    base_url="http://127.0.0.1:31415/v1",
    api_key="freellmapi-704878672ffd732da01727053c869683948f26decc0f8713"
)

llm_with_tools = llm.bind_tools(tools)

class State(MessagesState):
    pass

def call_model(state: State):
    response = llm_with_tools.invoke(
        state["messages"]
    )
    return {"messages": [response]}

tool_node = ToolNode(tools)

def should_continue(state:State):
    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tool"

    return END

builder = StateGraph(State)

builder.add_node("llm" , call_model)
builder.add_node("tool", tool_node)

builder.add_edge(START, "llm")
builder.add_conditional_edges(
    "llm",
    should_continue,
    {"tool":"tool" , END:END}
)
builder.add_edge("tool","llm")

graph = builder.compile()

'''
if __name__ == "__main__":
    result = graph.invoke(
        {"messages":[{"role":"user" , "content":"What is 25 multiplied by 8?"}]}
    )

    print(result)
'''
from langgraph.graph import START, END, StateGraph, MessagesState
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

class State(MessagesState):
    pass

@tool
def sum_num(a: int , b: int)->int:
    '''This functions get two number and give sum of them'''
    return a+b

tools = [sum_num]

llm = ChatOpenAI(
    model ="auto",
    base_url="http://127.0.0.1:31415/v1",
    api_key="freellmapi-704878672ffd732da01727053c869683948f26decc0f8713"
)

llm_with_tools = llm.bind_tools(tools)

def chat_llm(state:State):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

tool_node = ToolNode(tools)

def routing(state:State):
    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tool"
    return END

builder = StateGraph(State)

builder.add_node("llm", chat_llm)
builder.add_node("tool",tool_node)

builder.add_edge(START, "llm")
builder.add_conditional_edges(
    "llm",
    routing,
    {
        "tool":"tool",
        END:END
    }
)
builder.add_edge("tool","llm")
graph = builder.compile()

'''
if __name__ == "__main__":
    result = graph.invoke(
        {"messages":[{
            "role": "user",
            "content": "What is 134 plus 13"
        }]}
    )

    for message in result["messages"]:
        print(
            type(message).__name__,
            ":",
            message.content
        )
'''

from langgraph.graph import StateGraph, START, END , MessagesState
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI

class State (MessagesState):
    pass

@tool
def multiply(a: int, b :int) -> int:
    '''This function gets two number and returns multiplication of them'''
    return a*b
@tool
def add(a: int, b :int) -> int:
    '''This function gets two number and returns sum of them'''
    return a+b
@tool
def subtract(a: int, b :int) -> int:
    '''This function gets two number and returns subtrac of them'''
    return a-b

tools = [multiply, add, subtract]

tool_node = ToolNode(tools)

llm = ChatOpenAI(
    model = "auto",
    base_url= "http://127.0.0.1:31415/v1",
    api_key= "freellmapi-704878672ffd732da01727053c869683948f26decc0f8713"
)

llm_with_tools = llm.bind_tools(tools)

def chat_llm(state: State):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def routing(state : State):
    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tool"

    return END


builder = StateGraph(State)

builder.add_node("llm" , chat_llm)
builder.add_node("tool", tool_node)

builder.add_edge(START, "llm")
builder.add_conditional_edges(
    'llm',
    routing,
    {
        "tool": "tool",
        END: END
        }
)
builder.add_edge("tool", "llm")

graph = builder.compile()

'''
if __name__ == "__main__":
    result = graph.invoke(
        {"messages":[{
            "role": "user",
            "content": "What is 134 minus 13"
        }]}
    )

    for message in result["messages"]:
        print(
            type(message).__name__,
            ":",
            message.content
        )
'''
from langgraph.graph import START, END, StateGraph, MessagesState
from langgraph.checkpoint.memory import InMemorySaver
from langchain_openai import ChatOpenAI

class State(MessagesState):
    pass

llm = ChatOpenAI(
    model= "auto",
    base_url= "http://127.0.0.1:31415/v1",
    api_key= "freellmapi-704878672ffd732da01727053c869683948f26decc0f8713"
)

def chat_llm(state:State):
    result = llm.invoke(state["messages"])
    return{ "messages" : [result]}

builder = StateGraph(State)

builder.add_node("llm" , chat_llm)

builder.add_edge(START, "llm")
builder.add_edge("llm" , END)

checkpointer = InMemorySaver()

graph = builder.compile(checkpointer=checkpointer)

config = {
    "configurable":{
        "thread_id" : "thread_id"
    }
}

config2 = {
    "configurable": {
        "thread_id" : "another"
    }
}
'''
if __name__ == "__main__":
    result = graph.invoke(
        {"messages":[{
            "role": "user",
            "content": "my name is farshad"
        }]},
        config=config
    )
    result = graph.invoke(
        {"messages":[{
            "role": "user",
            "content": "What is my name"
        }]},
        config=config
    )

    for message in result["messages"]:
        print(
            type(message).__name__,
            ":",
            message.content
        )

    result = graph.invoke(
        {"messages":[{
            "role": "user",
            "content": "What is my name"
        }]},
        config=config2
    )

    for message in result["messages"]:
        print(
            type(message).__name__,
            ":",
            message.content
        )
'''


from langgraph.graph import START, END, StateGraph, MessagesState
from langgraph.checkpoint.memory import InMemorySaver
from langchain_openai import ChatOpenAI

class State(MessagesState):
    pass

llm = ChatOpenAI(
    model= "auto",
    base_url= "http://127.0.0.1:31415/v1",
    api_key= "freellmapi-704878672ffd732da01727053c869683948f26decc0f8713"
)

def chat_llm(state:State):
    result = llm.invoke(state["messages"])
    return{ "messages" : [result]}

builder = StateGraph(State)

builder.add_node("llm" , chat_llm)

builder.add_edge(START, "llm")
builder.add_edge("llm" , END)

checkpointer = InMemorySaver()

graph = builder.compile(checkpointer=checkpointer)

config = {
    "configurable":{
        "thread_id" : "thread_id"
    }
}
'''
result = graph.invoke(
    {"messages":[{
        "role": "user",
        "content": "my name is farshad"
    }]},
    config=config
)

result = graph.invoke(
    {"messages":[{
        "role": "user",
        "content": "ّI live in Mashhad"
    }]},
    config=config
)

result = graph.invoke(
    {"messages":[{
        "role": "user",
        "content": "ّwhich city I Live?"
    }]},
    config=config
)

for message in result["messages"]:
    print(
        type(message).__name__,
        ":",
        message.content
    )

history = list(graph.get_state_history(config))

old_config = history[5].config

result = graph.invoke(
    {"messages":[
        {"role": "user",
         "content": "I Live in Isfahan"
         }
    ]},
    config=old_config
)

for message in result["messages"]:
    print(
        type(message).__name__,
        ":",
        message.content
    )

result = graph.invoke(
    {"messages":[
        {"role": "user",
         "content": "which city I live?"
         }
    ]},
    config=config
)

for message in result["messages"]:
    print(
        type(message).__name__,
        ":",
        message.content
    )
'''

from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command


class State(TypedDict):
    order_id: str
    approved: bool
    result: str


def request_approval(state: State):

    decision = interrupt(
        {
            "question": "Do you approve cancellation?",
            "order_id": state["order_id"]
        }
    )

    return {
        "approved": decision
    }


def cancel_order(state: State):

    if state["approved"]:
        return {
            "result": f"Order {state['order_id']} cancelled."
        }

    return {
        "result": f"Order {state['order_id']} was NOT cancelled."
    }


builder = StateGraph(State)

builder.add_node(
    "approval",
    request_approval
)

builder.add_node(
    "cancel",
    cancel_order
)

builder.add_edge(
    START,
    "approval"
)

builder.add_edge(
    "approval",
    "cancel"
)

builder.add_edge(
    "cancel",
    END
)

checkpointer = InMemorySaver()

graph = builder.compile(
    checkpointer=checkpointer
)


config = {
    "configurable": {
        "thread_id": "order-123"
    }
}

'''
result = graph.invoke(
    {
        "order_id": "ORD-1001",
        "approved": False,
        "result": ""
    },
    config=config
)

print(result)

reslut  = graph.invoke(
    Command(resume= True),
    config=config
)

print(reslut)
'''
from typing import TypedDict
from langgraph.graph import START, END, StateGraph
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import InMemorySaver

class State(TypedDict):
    title:     str
    approved : str
    status :   str

def pub_decision(state: State):
    decision = interrupt(
        {
            "message" : "Do you Approve Publishing This Paper?"
        }
    )
    return {"approved" : decision}

def tell_status(state: State):
    if state["approved"]:
        return {"status": " The paper has been published!"}
    else:
        return{"status" : "The paper has benn rejected!"}

checkpoint = InMemorySaver()
builder = StateGraph(State)

builder.add_node("decision", pub_decision)
builder.add_node("status" , tell_status)

builder.add_edge(START, "decision")
builder.add_edge("decision" , "status")
builder.add_edge("status" , END)

config = {
    "configurable" :{
        "thread_id" : "1"
    }
}

config2 = {
    "configurable" :{
        "thread_id" : "2"
    }
}

graph = builder.compile(checkpointer=checkpoint)

'''
result = graph.invoke(
    {"title" : "The Best Curly Girl in the World!"},
    config=config)

print(result)

result2 = graph.invoke(
    Command(resume=True),
    config= config
)
print(result2)



result = graph.invoke(
    {"title" : "The Best Maryan Girl in the World!"},
    config=config2)

print(result)

result2 = graph.invoke(
    Command(resume=False),
    config= config2
)
print(result2)
'''


from typing import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

llm = ChatOpenAI(
    model="auto",
    base_url= "http://127.0.0.1:31415/v1",
    api_key= "freellmapi-704878672ffd732da01727053c869683948f26decc0f8713"
)


class State(TypedDict):
    resume        : str
    info_extracted: str
    summary       : str
    improved      : str

def info_extraction(state: State):
    resume = state["resume"]

    response = llm.invoke(
        f'''
        Role: You are an expert Resume Parser.
        Task: Extract key professional information from the raw resume text provided below.
        Instructions:
        Carefully analyze the text and group the extracted details into three clear categories: Skills, Education, and Experience.
        For Skills: List hard skills, soft skills, tools, and technologies.
        For Education: Extract degrees, institutions, and graduation years.
        For Experience: List job titles, company names, durations, and key responsibilities/achievements.
        Do NOT summarize or improve the content; extract the facts directly and accurately.
        Input Resume:
        {resume}
        Output Format:
        "skills": [...],
        "education": [...],
        "experience": [...]       
        '''
    )

    return {"info_extracted" : response.content}

def cv_summary(state: State):
    extracted_data = state["info_extracted"]

    response = llm.invoke(
        f'''
        Role: You are a Professional Career Counselor.
        Task: Synthesize the extracted resume data into a concise, high-impact career summary.
        Instructions:
        Use the structured data provided from the extraction step (Skills, Education, Experience).
        Draft a brief executive summary (2-3 sentences max).
        Highlight the core area of expertise, total experience/seniority level, key accomplishments, and overall career focus.
        Keep the tone factual, objective, and professional.
        Input Data:
        {extracted_data}
        Output Format:
        Provide a plain text summary without bullet points or unnecessary introduction.
        '''
    )

    return {"summary" : response.content}

def improvement(state: State):
    summary_text = state["summary"]

    response = llm.invoke(
        f'''
        Role: You are a Senior HR Specialist and Resume Optimization Expert.
        Task: Transform the provided raw summary into an outstanding, job-winning Professional Profile / Summary Statement for a resume.
        Instructions:
        Reframe the summary using strong action verbs, dynamic industry language, and clear value propositions.
        Optimize the phrasing to highlight problem-solving abilities, quantifiable business impact, and technical strengths.
        Maintain maximum professional impact while staying true to the candidate's original background.
        Generate 2 different versions:
        Version A (Impact & Action-Oriented): Focuses heavily on results, efficiency, and execution.
        Version B (Strategic & Domain-Focused): Focuses on core competencies, strategic growth, and domain knowledge.
        Input Summary:
        {summary_text}
        Output Format:
        Option 1 (Impact-Driven):
        [Generated Profile]
        Option 2 (Strategic):
        [Generated Profile]
        '''
    )

    return {"improved" : response.content}

builder = StateGraph(State)

builder.add_node("extract" , info_extraction)
builder.add_node("summary" , cv_summary)
builder.add_node("improve"  , improvement)

builder.add_edge(START, "extract")
builder.add_edge("extract" , "summary")
builder.add_edge("summary" , "improve")
builder.add_edge("improve" , END)

graph = builder.compile()

'''
if __name__ == "__main__":
    sample_resume = """
    John Doe
    Data Scientist & Machine Learning Engineer
    Email: john.doe@email.com | Phone: +1-555-019-2834 | LinkedIn: linkedin.com/in/johndoe-sample
    Education
    Master of Science in Computer Science – Tech University (2020 – 2022) | GPA: 3.8/4.0
    Bachelor of Science in Software Engineering – State University (2016 – 2020)
    Work Experience
    Senior Data Analyst | DataCorp Solutions (Jan 2023 – Present)
    Built end-to-end Machine Learning pipelines using Python, Scikit-Learn, and SQL to predict customer churn, reducing churn rate by 14%.
    Designed automated dashboard workflows with Power BI and PostgreSQL for real-time reporting to stakeholders.
    Fine-tuned LLM models for customer support ticket classification, improving auto-routing accuracy by 25%.
    Junior Software Developer | Innovate Tech (Jun 2020 – Dec 2022)
    Developed RESTful APIs using FastAPI and PostgreSQL to support microservices architecture.
    Collaborated with cross-functional teams to integrate Docker and CI/CD pipelines into deployment workflows.
    Processed and cleaned large structured datasets using Pandas and PySpark.
    Skills & Tools
    Programming Languages: Python, SQL, TypeScript
    Frameworks & Libraries: FastAPI, Scikit-Learn, PyTorch, Pandas, NumPy
    Databases & Tools: PostgreSQL, Docker, Git, Power BI, Redis
    Soft Skills: Problem-solving, Technical Communication, Agile Methodology
    """

    result = graph.invoke({"resume": sample_resume})

    # === چاپ تمیز خروجی‌ها ===
    print("\n" + "="*50)
    print(" 📌 STEP 1: EXTRACTED DATA")
    print("="*50)
    print(result.get("info_extracted"))

    print("\n" + "="*50)
    print(" 📌 STEP 2: SUMMARY")
    print("="*50)
    print(result.get("summary"))

    print("\n" + "="*50)
    print(" 📌 STEP 3: IMPROVED PROFILE")
    print("="*50)
    print(result.get("improved"))
    print("="*50 + "\n")

'''

from typing import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import START, END, StateGraph


class State(TypedDict):
    product_description: str
    marketing_analysis : str
    customer_analysis  : str
    technical_analysis : str
    report             : str


llm = ChatOpenAI(
    model="auto",
    base_url="http://127.0.0.1:31415/v1",
    api_key="freellmapi-704878672ffd732da01727053c869683948f26decc0f8713"
)

def technical_analysis(state: State):
    product_descriptoin = state["product_description"]
    prompt = f'''
        تو یک مهندس ارشد محصول و متخصص بررسی فنی (Technical Product Analyst) هستی.
        وظیفه تو تحلیل ویژگی‌های فنی محصول بر اساس متن ورودی است. متمرکز بر زیرساخت، امکان‌پذیری فنی، معماری و مقیاس‌پذیری باش و وارد بحث‌های بازاریابی یا احساسات مشتری نشو.
        متن شرح محصول:
        {product_descriptoin}
        لطفا بررسی خود را در قالب بخش‌های زیر ارائه بده:
        ۱. مشخصات و قابلیت‌های فنی اصلی (Core Technical Features): استخراج دقیق فناوری‌ها و توانمندی‌های ذکر شده.
        ۲. امکان‌پذیری و پیچیدگی پیاده‌سازی (Feasibility & Complexity): چالش‌های فنی احتمالی در توسعه، نگهداری یا مقیاس‌پذیری.
        ۳. نقاط قوت و ضعف فنی (Technical Pros & Cons): لیست کوتاه از برجستگی‌ها و محدودیت‌های معماری/فنی.
        ۴. نیازمندی‌های پیش‌فرض (Dependencies & Prerequisite): ابزارها، زیرساخت‌ها یا سیستم‌هایی که برای کارکرد این محصول ضروری هستند.
    '''
    result = llm.invoke(prompt)
    return {"technical_analysis" : result.content}

def marketing_analysis(state: State):
    product_descriptoin = state["product_description"]
    prompt = f'''
        تو یک استراتژیست ارشد بازاریابی و رشد محصول (Product Marketing Strategist) هستی.
        وظیفه تو تحلیل جنبه‌های تجاری، موقعیت‌سنجی در بازار و پتانسیل فروش محصول بر اساس متن ورودی است. فقط روی بازار و ارزش پیشنهادی تمرکز کن و وارد مباحث عمیق فنی نشو.
        متن شرح محصول:
        {product_descriptoin}
        لطفا بررسی خود را در قالب بخش‌های زیر ارائه بده:
        ۱. ارزش پیشنهادی یکتا (Unique Value Proposition - UVP): چه چیزی این محصول را در بازار متمایز می‌کند؟
        ۲. پرسونای مخاطب هدف (Target Audience): این محصول دقیقاً چه بازار یا گروهی از مشتریان/کسب‌وکارها را هدف گرفته است؟
        ۳. مزیت رقابتی و موانع ورود (Competitive Advantage & Position): پتانسیل محصول در رقابت با راه‌حل‌های موجود در بازار.
        ۴. پیشنهادهای بهبود مارکتینگ (GTM Strategies): پیام‌های کلیدی بازاریابی یا کانال‌های پیشنهادی برای جذب کاربر.
    '''
    result = llm.invoke(prompt)
    return {"marketing_analysis" : result.content}

def customer_analysis(state: State):
    product_descriptoin = state["product_description"]
    prompt = f'''
        تو یک متخصص تجربه مشتری (CX Specialist) و مدافع حقوق کاربر (User Advocate) هستی.
        وظیفه تو بررسی محصول از زاویه‌دید کاربر نهایی است. تمرکز تو باید روی میزان سادگی، حل مسئله کاربر، دردسرهای احتمالی (Pain Points) و ارزش عملیاتی باشد.
        متن شرح محصول:
        {product_descriptoin}
        لطفا بررسی خود را در قالب بخش‌های زیر ارائه بده:
        ۱. نقاط درد حل‌شده (User Pain Points Addressed): این محصول کدام مشکالات و دغدغه‌های روزمره کاربر را برطرف می‌کند؟
        ۲. تجربه کاربری و سادگی استفاده (UX & Ease of Use): بر اساس شرح موجود، استفاده از این محصول چقدر برای کاربر راحت یا پیچیده خواهد بود؟
        ۳. ارزش دریافتی کاربر (Perceived Value): چرا یک کاربر باید تمایل به استفاده یا خرید این محصول داشته باشد؟
        ۴. ریسک‌ها و ناامیدی‌های احتمالی کاربر (Potential User Frustrations): چه مواردی ممکن است باعث سوءتفاهم، نارضایتی یا ریزش کاربر شود؟
    '''
    result = llm.invoke(prompt)
    return {"customer_analysis" : result.content}

def final_report(state:State):
    result = f'''
    بررسی از جنبه مشتری:
    {state["customer_analysis"]}
    ---------------------------------------------
    بررسی از جنبه فنی:
    {state["technical_analysis"]}
    ---------------------------------------------

    بررسی از جنبه بازاریابی:
    {state["marketing_analysis"]}
    ---------------------------------------------
    '''
    return {"report": result}


builder = StateGraph(State)

builder.add_node("marketing", marketing_analysis)
builder.add_node("customer" , customer_analysis)
builder.add_node("technical", technical_analysis)
builder.add_node("report", final_report)

builder.add_edge(START, "marketing")
builder.add_edge(START, "customer")
builder.add_edge(START, "technical")
builder.add_edge("marketing", "report")
builder.add_edge("customer", "report")
builder.add_edge("technical", "report")

graph = builder.compile()
""" __name__ == "__main__":
    description='''
    سامانه ConstructAI یک پلتفرم تحت وب و اپلیکیشن موبایل مبتنی بر هوش مصنوعی است که برای مدیریت خودکار پروژه‌های ساخت‌وساز و مدیریت پیمانکاران طراحی شده است.
    این سیستم از طریق اتصال API به دوربین‌های IP موجود در کارگاه‌های عمرانی، تصویر پردازش‌شده پروژه را در لحظه تحلیل می‌کند. مدل‌های پردازش تصویر (Computer Vision) آموزش‌دیده در این پلتفرم، میزان پیشرفت فیزیکی پروژه را با فایل‌های سه‌بعدی BIM (مدل‌سازی اطلاعات ساختمان) و گانت‌چارت اولیه مقایسه کرده و در صورت انحراف از زمان‌بندی یا وقوع تخلفات ایمنی (مانند نپوشیدن کلاه ایمنی یا ورود به مناطق خطرناک)، به صورت هوشمند هشدار صادر می‌کنند.
    همچنین، پلتفرم دارای یک ماژول چت‌بات صوتی و متنی متصل به مدل‌های بزرگ زبانی (LLM) است که کارگران و مهندسان ناظر می‌توانند گزارش‌های روزانه کارگاهی را به صورت فایل صوتی یا متن ارسال کنند. سیستم این گزارش‌ها را پردازش کرده، صورت‌جلسه‌ها را تنظیم می‌نماید و داده‌ها را در دیتابیس PostgreSQL ذخیره و تحلیل می‌کند.
    مخاطبان هدف: شرکت‌های پیمانکاری متوسط و بزرگ، مدیران پروژه‌های ساختمانی و سرمایه‌گذاران ملک که به دنبال کاهش هزینه‌های ناشی از تاخیر در پروژه، افزایش امنیت جانی نیروی کار و حذف گزارش‌دهی‌های کاغذی و دستی هستند.
    ویژگی‌های کلیدی:
    تحلیل و ردیابی لحظه‌ای پیشرفت فیزیکی ساخت‌وساز با پردازش تصویر دوربین‌ها
    تشخیص خودکار خطرات ایمنی کارگاه و اعلام هشدار آنی روی اپلیکیشن موبایل مدیران
    تبدیل گزارش‌های صوتی مهندسان به داده‌های ساختاریافته پروژه‌ای و صورت‌جلسه
    داشبورد مدیریتی پیش‌بینی هزینه‌ها و محاسبه زمان نهایی اتمام پروژه بر اساس سرعت پیشرفت واقعی
    قابلیت کارکرد آفلاین اپلیکیشن موبایل برای ثبت داده در نقاط بدون اینترنت و همگام‌سازی (Sync) پس از اتصال
    '''

    result = graph.invoke({"product_description":description})

    print(result["report"])
"""

from pydantic import BaseModel
from typing import Literal, TypedDict, Optional
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START
from langgraph.types import Command

class State(TypedDict):
    request  : str
    category : Optional[str] = None
    response : Optional[str] = None

class RouteCategory(BaseModel):
    category: Literal[
        "business",
        "technical",
        "general"
    ]

llm = ChatOpenAI(
    model="auto",
    base_url="http://127.0.0.1:31415/v1",
    api_key= "freellmapi-704878672ffd732da01727053c869683948f26decc0f8713"
)

llm_structured = llm.with_structured_output(RouteCategory)

def categorizing(state:State):
    user_request = state["request"]
    prompt = f'''
        You are a recruitment request routing system.
        Classify the recruitment request into exactly one of these categories:
        technical
        business
        general

        Rules:
        technical:
        Requests related to technical hiring, including software developers, engineers, programmers, technical skills, programming languages, frameworks, databases, cloud infrastructure, DevOps, data science, cybersecurity, or other technical roles and requirements.
        business:
        Requests related to business hiring, including sales, marketing, finance, accounting, HR, operations, management, customer success, business development, or other non-technical business roles and requirements.
        general:
        Any other recruitment request that does not clearly belong to the technical or business category.

        Recruitment request:
        {user_request}
    '''
    result = llm_structured.invoke(prompt)
    return {"category": result.category }

def routing_function(state:State):
    return state["category"]

def technical_request(state:State):
    return {"response" : "Your Technical Request Has been Received!"}

def business_request(state:State):
    return {"response" : "Your Business Request Has been Received!"}

def general_request(state:State):
    return {"response" : "Your General Request Has been Received!"}

builder = StateGraph(State)

builder.add_node("category", categorizing)
builder.add_node("business", business_request)
builder.add_node("technical", technical_request)
builder.add_node("general", general_request)

builder.add_edge(START,"category")
builder.add_conditional_edges(
    "category",
    routing_function,
    {
        "business":"business",
        "technical":"technical",
        "general":"general"
    }
)
builder.add_edge("business" , END)
builder.add_edge("technical" , END)
builder.add_edge("general" , END)

graph = builder.compile()

'''
if __name__ == "__main__":
    result = graph.invoke({"request": "من یه برنامه نویس پایتون میخوام"})
    print(result)  
'''

from pydantic import BaseModel
from typing import Literal, TypedDict, Optional
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START
from langgraph.types import Command

class State(TypedDict):
    request  : str
    category : Optional[str] = None
    response : Optional[str] = None

class RouteCategory(BaseModel):
    category: Literal[
        "business",
        "technical",
        "general"
    ]

llm = ChatOpenAI(
    model="auto",
    base_url="http://127.0.0.1:31415/v1",
    api_key= "freellmapi-704878672ffd732da01727053c869683948f26decc0f8713"
)

llm_structured = llm.with_structured_output(RouteCategory)

def categorizing(state:State)-> Command[Literal ["technical","business","general"]]:
    user_request = state["request"]
    prompt = f'''
        You are a recruitment request routing system.
        Classify the recruitment request into exactly one of these categories:
        technical
        business
        general

        Rules:
        technical:
        Requests related to technical hiring, including software developers, engineers, programmers, technical skills, programming languages, frameworks, databases, cloud infrastructure, DevOps, data science, cybersecurity, or other technical roles and requirements.
        business:
        Requests related to business hiring, including sales, marketing, finance, accounting, HR, operations, management, customer success, business development, or other non-technical business roles and requirements.
        general:
        Any other recruitment request that does not clearly belong to the technical or business category.

        Recruitment request:
        {user_request}
    '''
    result = llm_structured.invoke(prompt)

    if result.category == "technical":
        return Command(
                update={"category": result.category},
                goto= "technical"
        )

    if result.category == "business":
        return Command(
                update={"category": result.category},
                goto= "business"
        )

    if result.category == "general":
        return Command(
                update={"category": result.category},
                goto= "general"
        )

def technical_request(state:State):
    return {"response" : "Your Technical Request Has been Received!"}

def business_request(state:State):
    return {"response" : "Your Business Request Has been Received!"}

def general_request(state:State):
    return {"response" : "Your General Request Has been Received!"}

builder = StateGraph(State)

builder.add_node("category", categorizing)
builder.add_node("business", business_request)
builder.add_node("technical", technical_request)
builder.add_node("general", general_request)

builder.add_edge(START,"category")
builder.add_edge("business" , END)
builder.add_edge("technical" , END)
builder.add_edge("general" , END)

graph = builder.compile()

'''
if __name__ == "__main__":
    result = graph.invoke({"request": "من یه متخصص مارکتینگ میخوام"})
    print(result)  
'''

from typing import TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, START,END
from langgraph.types import Send


class State(TypedDict):
    topic: str
    sections: list[str]
    result: Annotated[list[str],operator.add]
    final_report: str

class WorkerState(TypedDict):
    section : str

def orchestrator(state: State):
    sections = [
        "Historical Background",
        "Current Situation",
        "Future Outlook"
    ]
    return {"sections" : sections}

def create_worker(state:State):
    return [
        Send(
            "worker",
            {"section" : section}
        ) for section in state["sections"]
    ]

def worker(state: WorkerState):
    section = state["section"]

    result = f"Research result for: {section}"

    return {"result" : [result]}

def gathering(state:State):
    return {}
    
def synthesizer (state: State):
    result = "\n\n". join(state["result"])

    return {"final_report" : result}

builder = StateGraph(State)

builder.add_node("orchestrator", orchestrator)
builder.add_node("worker", worker)
builder.add_node("synthesizer" , synthesizer)
builder.add_node("gather", gathering)

builder.add_edge(START, "orchestrator")
builder.add_conditional_edges(
    "orchestrator",
    create_worker,
    ["worker"]
)
builder.add_edge("worker" , "gather")
builder.add_edge("gather" , "synthesizer")
builder.add_edge("synthesizer", END)

graph = builder.compile()
result  = graph.invoke({"topic" :"House"})

print(result["final_report"])
