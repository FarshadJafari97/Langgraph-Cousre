from langgraph.graph import StateGraph, END, START
from typing import TypedDict
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model = "auto",
    base_url= "http://127.0.0.1:31415/v1",
    api_key= "freellmapi-704878672ffd732da01727053c869683948f26decc0f8713"
)

#--------------------------------------------------------------------------
# Evaluation SubGraph
#--------------------------------------------------------------------------
class Approval(TypedDict):
    question : str
    answer   : str
    approved : bool

class InputApproval(TypedDict):
    question : str
    answer   : str

class OutputApproval(TypedDict):
    approved : bool

llm_approval = llm.with_structured_output(OutputApproval)

def evaluation (state:Approval):
    question = state["question"]
    answer   = state["answer"]
    prompt = f'''
    در ادامه یک سوال و یک پاسخ برات میاد. آن‌ها را بررسی کن و بگو که آیا آن را تایید میکنی یا نه
    سوال :
    {question}
    جواب :
    {answer}
    '''
    result  =llm_approval.invoke(prompt)
    return  result

builder  = StateGraph(
    state_schema=Approval,
    input_schema=InputApproval,
    output_schema=OutputApproval
)

builder.add_node("eval", evaluation)

builder.add_edge(START, "eval")
builder.add_edge("eval" , END)

eval_graph = builder.compile()
#--------------------------------------------------------------------------
# Answer Graph
#--------------------------------------------------------------------------
class State(TypedDict):
    question : str
    answer   : str
    approved : bool


def answer (state:State):
    question = state['question']
    prompt = f'''
    تو باید به سوال زیر پاسخ بدی، هیچ توضیح اضافه ای نده
    سوال :
    {question}
    '''
    result = llm.invoke(prompt)
    return {"answer" : result.content}

def routing_function(state:State):
    status = state["approved"]
    if status:
        return "ok"
    if not status:
        return "nok"

builder = StateGraph(State)

builder.add_node("answer", answer)
builder.add_node("eval" , eval_graph)

builder.add_edge(START, "answer")
builder.add_edge("answer" , "eval")
builder.add_conditional_edges(
    "eval",
    routing_function,
    {
        "ok"  : END,
        "nok" : "answer"
    }
)

main_graph = builder.compile()

'''
result = main_graph.invoke(
    {
        "question" : "Give me the list of Irab's presindesnts"
    }
)
print(result)
'''

#--------------------------------------------------------------------------
# Same But with Command in Subgraphs
#--------------------------------------------------------------------------
from langgraph.types import Command
#--------------------------------------------------------------------------
# Evaluation SubGraph
#--------------------------------------------------------------------------
class Approval(TypedDict):
    question : str
    answer   : str
    approved : bool

class InputApproval(TypedDict):
    question : str
    answer   : str

class OutputApproval(TypedDict):
    approved : bool

llm_approval = llm.with_structured_output(OutputApproval)

def evaluation (state:Approval):
    question = state["question"]
    answer   = state["answer"]
    prompt = f'''
    در ادامه یک سوال و یک پاسخ برات میاد. آن‌ها را بررسی کن و بگو که آیا آن را تایید میکنی یا نه
    سوال :
    {question}
    جواب :
    {answer}
    '''
    result  =llm_approval.invoke(prompt)

    if result["approved"]:
        return  Command(
            update={"approved" : True},
            goto=END,
            graph=Command.PARENT
        )
    if not result["approved"]:
        return  Command(
            update={"approved" : False},
            goto="answer",
            graph=Command.PARENT
        )

builder  = StateGraph(
    state_schema=Approval,
    input_schema=InputApproval,
    output_schema=OutputApproval
)

builder.add_node("eval", evaluation)

builder.add_edge(START, "eval")
builder.add_edge("eval" , END)

eval_graph = builder.compile()
#--------------------------------------------------------------------------
# Answer Graph
#--------------------------------------------------------------------------
class State(TypedDict):
    question : str
    answer   : str
    approved : bool


def answer (state:State):
    question = state['question']
    prompt = f'''
    تو باید به سوال زیر پاسخ بدی، هیچ توضیح اضافه ای نده
    سوال :
    {question}
    '''
    result = llm.invoke(prompt)
    return {"answer" : result.content}

builder = StateGraph(State)

builder.add_node("answer", answer)
builder.add_node("eval" , eval_graph)

builder.add_edge(START, "answer")
builder.add_edge("answer" , "eval")

main_graph = builder.compile()

'''
result = main_graph.invoke(
    {
        "question" : "Give me the list of Irab's presindesnts"
    }
)
print(result)
'''
#--------------------------------------------------------------------------
# Command in Different paths Subgraph
#--------------------------------------------------------------------------
from typing import TypedDict
from langgraph.types import Command
from langgraph.graph import START, END, StateGraph
#--------------------------------------------------------------------------
# Validation Subgraph
#--------------------------------------------------------------------------
class ValidationState(TypedDict):
    amount   : float

def validation(state:ValidationState):
    amount = state["amount"]

    if amount>0:
        return Command(
            update={
                "status" : "Valid"
            },
            goto="success",
            graph=Command.PARENT
        )

    if amount<0:
        return Command(
            update={"status" : "Not Valid"},
            goto= "failure",
            graph=Command.PARENT

        )

builder = StateGraph(ValidationState)

builder.add_node("validation" , validation)

builder.add_edge(START, "validation")

validation_graph = builder.compile()
#--------------------------------------------------------------------------
# Main Graph
#--------------------------------------------------------------------------

class State(TypedDict):
    order_id : str
    amount   : float
    status   : str
    message  : str

def success(state:State):
    return {
        "message" : "This is Valid"
    }

def failure(state:State):
    return {
        "message" : "This Not Valid"
    }

builder = StateGraph(State)

builder.add_node("valid" , validation_graph)
builder.add_node("success" , success)
builder.add_node("failure" , failure)

builder.add_edge(START, "valid")
builder.add_edge("success" , END)
builder.add_edge("failure" , END)

main_graph = builder.compile()

result = main_graph.invoke(
    {
        "order_id" : "HS-21",
        "amount"   : -23
    }
)
print(result)
