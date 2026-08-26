from langchain_openai import ChatOpenAI
from langgraph.func import entrypoint, task
from langchain.tools import tool
from langgraph.prebuilt import ToolNode

@tool
def add(a:int, b:int):
    '''This function get 2 number and return summation'''
    c = a + b 
    return c

@tool
def subtract(a:int , b:int):
    '''This function get 2 number and return sutract'''
    c = a - b
    return c

@tool
def multiply(a:int, b:int):
    '''This function get 2 number and return multiplication'''
    c = a * b
    return c

tools= [add, subtract, multiply]

llm = ChatOpenAI(
    model="auto",
    base_url= "http://127.0.0.1:31415/v1",
    api_key= "freellmapi-704878672ffd732da01727053c869683948f26decc0f8713"
)

llm_with_tools = llm.bind_tools(tools)

tool_node = ToolNode(tools)

@task
def answer(prompt : str):
    result = llm_with_tools.invoke(prompt)
    return result

@entrypoint()
def answering_math_question(prompt: str):

    ai_message = answer(prompt).result()

    tool_result = tool_node.invoke({
        "messages": [ai_message]
    })

    final_result = llm_with_tools.invoke(
        [ai_message] + tool_result["messages"]
    )

    return final_result

result = answering_math_question.invoke("۱۰ به علاوه ۳ چند میشه")
print(result)