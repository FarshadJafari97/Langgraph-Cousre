# -------------------------------------------------------------------
# LLM Approves the Result
#--------------------------------------------------------------------
from typing import TypedDict, Optional
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START

class State(TypedDict):
    question : str
    answer   : str
    approved : bool
    feedback : str

class Approval(TypedDict):
    approved : bool
    feedback : str

llm = ChatOpenAI(
    model= "auto",
    base_url= "http://127.0.0.1:31415/v1",
    api_key= "freellmapi-704878672ffd732da01727053c869683948f26decc0f8713"
)

llm_eval = llm.with_structured_output(Approval)

def answer_question(state:State):
    question = state["question"]
    feedback = state.get("feedback","")
    prompt = f'''
    در پاسخ فقط به سوال زیر جواب بده و هیچ توضیح اضافه دیگری نده!
    سوال:
    {question}
    اگه در زیر متنی آمده باشد به این معنی است که جواب قبلی اشتباه بوده و باید اصلاح شود:
    {feedback}
    '''
    result = llm.invoke(prompt)
    return{
        "answer" : result.content
    }

def eval_answer(state:State):
    question = state["question"]
    answer   = state["answer"]
    feedback = state.get("feedback","")

    prompt =f'''
    سوال و پاسخ زیر رو بررسی کن و بگو که آیا تایید میکنی که سوال به درستی پاسخ داده شده است یا نه
    سوال:
    {question}
    جواب :
    {answer}
    اگه در زیر متنی آمده باشد به این معنی است که این سوال یه بار رد شده و الان دوباره پاسخ داده شده و متن زیر فیدبک است
    {feedback}
    در نهایت بعد از تایید یا رد به آن فیدبک بده
    '''
    result = llm_eval.invoke(prompt)

    return result

def routing_function(state:State):
    approved = state["approved"]

    if approved:
        return "approved"
    if not approved:
        return "not_approved"

builder = StateGraph(State)

builder.add_node("answer", answer_question)
builder.add_node("eval"  , eval_answer)

builder.add_edge(START, "answer")
builder.add_edge("answer" ,"eval")
builder.add_conditional_edges(
    "eval",
    routing_function,
    {
        "approved" : END,
        "not_approved" : "answer"
    }
)

'''
graph = builder.compile()
result = graph.invoke({
    "question" : "چقدر درخت در دنیا وجود دارد"
}
)
print(result)
'''
# -------------------------------------------------------------------
# LLM Scores the Result
#--------------------------------------------------------------------
from typing import TypedDict
from langchain_openai import ChatOpenAI
import json

class State(TypedDict):
    question      : str
    answer        : str
    feedback      : str
    overall_score : int

class Eval(TypedDict):
    accuracy      : int
    completeness  : int
    clarity       : int
    overall_score : int
    feedback      : str

llm = ChatOpenAI(
    model= "auto",
    base_url= "http://127.0.0.1:31415/v1",
    api_key= "freellmapi-704878672ffd732da01727053c869683948f26decc0f8713"
)

llm_eval = llm.with_structured_output(Eval)

def answer_question(state:State):
    question = state["question"]
    feedback = state.get("feedback","")
    prompt = f'''
    در پاسخ فقط به سوال زیر جواب بده و هیچ توضیح اضافه دیگری نده!
    سوال:
    {question}
    اگه در زیر متنی آمده باشد به این معنی است که جواب قبلی اشتباه بوده، این فیدبک آن است و باید اصلاح شود در غیر این صورت دفعه اول است که داریه به این سوال پاسخ میدی
    {feedback}
    '''
    result = llm.invoke(prompt)
    return{
        "answer" : result.content
    }

def eval_answer(state:State):
    question = state["question"]
    answer   = state["answer"]
    feedback = state.get("feedback","")
    prompt =f'''
    سوال و پاسخ زیر رو بررسی کن و بگو که آیا تایید میکنی که سوال به درستی پاسخ داده شده است یا نه
    سوال:
    {question}
    جواب :
    {answer}
    اگه در زیر متنی آمده باشد به این معنی است که این سوال یه بار رد شده و الان دوباره پاسخ داده شده و متن زیر فیدبک است
    {feedback}
    در نهایت بعد از امتیا دادن ز  به آن فیدبک بده
    '''
    output = llm_eval.invoke(prompt)
    result = json.dumps(output, ensure_ascii=False, indent=2)

    return {
        "feedback" : result,
        "overall_score" : output["overall_score"]
    }

def routing_function(state:Eval):
    overall_score = state["overall_score"]

    if overall_score>5:
        return "approved"
    if overall_score<=5:
        return "not_approved"


builder = StateGraph(State)

builder.add_node("answer", answer_question)
builder.add_node("eval"  , eval_answer)

builder.add_edge(START, "answer")
builder.add_edge("answer" ,"eval")
builder.add_conditional_edges(
    "eval",
    routing_function,
    {
        "approved" : END,
        "not_approved" : "answer"
    }
)

graph = builder.compile()
result = graph.invoke({
    "question" : "چقدر درخت در دنیا وجود دارد"
}
)
print(result)