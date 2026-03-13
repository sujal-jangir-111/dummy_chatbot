from langgraph.graph import StateGraph, START, END
from typing import TypedDict,Literal,Annotated
from langchain_core.messages import SystemMessage,HumanMessage,BaseMessage 
#from langgraph.checkpoint.memory import InMemorySaver  #(stort term memory , store data in ram | lost data when we refresh the page)
from langgraph.checkpoint.memory import InMemorySaver
import sqlite3
from langgraph.graph.message import add_messages


import os
from dotenv import load_dotenv

# load environment variables
load_dotenv()

from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)


class ChatState(TypedDict):

    messages : Annotated[list[BaseMessage], add_messages]



def chat_node(state:ChatState):
    messages = state["messages"]
        
    response = llm.invoke(messages)

    return {"messages" : [response]}





graph = StateGraph(ChatState)


#conn=sqlite3.connect(database="chatbot.db", check_same_thread=False)     #connecting database to checkpointer
checkpointer = InMemorySaver()


graph.add_node("chat_node",chat_node)

graph.add_edge(START, "chat_node")
graph.add_edge("chat_node",END)





chatbot = graph.compile(checkpointer = checkpointer)




def retrieve_all_threads():
    all_threads = set()

    for cp in checkpointer.list(None):
        all_threads.add(cp.config["configurable"]["thread_id"])

    return list(all_threads)


#print(retrive_all_threads())



# #TEST : 
# CONFIG = {"configurable":{"thread_id" : "thread-2"}}

# result = chatbot.invoke(
#                 {"messages" : [HumanMessage(content = "how to make pasta")]},
#                 config=CONFIG,
#                 stream_mode = "messages"
#             )


#print(chatbot.get_state(config = CONFIG).values["messages"])












# #straming
if __name__ == "__main__":
    user_input = input("Enter your message: ")
    for message_chunk, metadata in chatbot.stream(
        {"messages" : [HumanMessage(content = user_input)]},
        config= {"configurable":{"thread_id":"1"}},
        stream_mode = "messages"
    ):
        if message_chunk.content:
            print(message_chunk.content, end=" ", flush = True)





















