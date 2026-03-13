import streamlit as st
from backend import chatbot
from backend import retrieve_all_threads

from langchain_core.messages import HumanMessage 
import uuid



#{"role" : "user", "content":"hi"}
#{"role" : "assistant", "content":"hi"}


def generate_thread():
    return uuid.uuid4()

def add_thread(thread_id):
    if thread_id not in st.session_state["chat_thread"]:
        st.session_state["chat_thread"].append(thread_id)

def reset_chat():
    st.session_state["thread_id"] = generate_thread()
    st.session_state["message_history"] = []
    add_thread(st.session_state["thread_id"])           #add thread in in chat history when new chat is clicked


if "chat_thread" not in st.session_state:      # this is for thread id of current session
    st.session_state["chat_thread"] = retrieve_all_threads()  



    
# def load_conversation_code(thread_id):
#     return chatbot.get_state({"configurable" : {"thread_id" : thread_id}}).values["messages"]
def load_conversation_code(thread_id):
    state = chatbot.get_state({"configurable": {"thread_id": thread_id}})
    return state.values.get("messages", [])




if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread()     #this is defauld thred id when page opens (and this is the thread id of current session)

add_thread(st.session_state["thread_id"])            ##this is defauld thred id when page opens to save in chat thread history




if "message_history" not in st.session_state:
    st.session_state["message_history"] = []    






st.sidebar.title("Langgraph Chatbot")

if st.sidebar.button("New Chat"):
    reset_chat()

st.sidebar.header("My Conversations")

# for thread_id in st.session_state["chat_thread"]:
#     st.sidebar.button(str(thread_id))
for thread_id in st.session_state["chat_thread"]:
    if st.sidebar.button(str(thread_id)):
        st.session_state["thread_id"] = thread_id
        messages = load_conversation_code(thread_id)

        temp_messages=[]

        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = "user"
            else:
                role = "assistant"
            temp_messages.append({"role" : role, "content" : msg.content})

        st.session_state["message_history"] = temp_messages








for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])


CONFIG = {"configurable":{"thread_id" : st.session_state["thread_id"]}}





user_input = st.chat_input("Type here")

if user_input:

    st.session_state["message_history"].append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.text(user_input)

    with st.chat_message("assistant"):

        def response_generator():
            full_response = ""

            try:
                for message_chunk, metadata in chatbot.stream(
                    {"messages": [HumanMessage(content=user_input)]},
                    config=CONFIG,
                    stream_mode="messages"
                ):

                    if message_chunk.content:
                        full_response += message_chunk.content
                        yield message_chunk.content

                st.session_state["message_history"].append(
                    {"role": "assistant", "content": full_response}
                )

            except Exception as e:
                st.error(f"Error generating response: {e}")

        st.write_stream(response_generator())





