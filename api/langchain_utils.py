from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from typing import List
from langchain_core.documents import Document
import os
from chroma_utils import vectorstore

retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

output_parser = StrOutputParser()


#setting up Prompts
contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."   
)

contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", contextualize_q_system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

# qa_prompt = ChatPromptTemplate.from_messages([
#     ("system", "You are a helpful AI assistant. Use the following context to answer the user's question."),
#     ("system", "Context: {context}"),
#     MessagesPlaceholder(variable_name="chat_history"),
#     ("human", "{input}")
# ])
qa_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a specialized school information assistant with the following guidelines:

PRIMARY FUNCTION:
- Firstly greet the user and ask how you can help with a confortable emoji and let the user reply before any other thing If it is a new conversation
- Assist parents with school-related inquiries and requests
- List out all school-related inquiries from the context you can find in the database
- Don't answer the queries until you look at the context 
- Provide friendly, clear, and accurate responses
- remove unneccesary symbols and characters from your responses and align the text well and structured
- If you can't find any information for the user's queries simply tell the user that that the information is not available
- If the user haven't asked about a particular question before, don't use it as a follow up question
- Listen carefully to understand parent needs
- Ask clarifying questions when needed
- Guide users to appropriate school resources
- End each response positively

CONSTRAINTS:
- Only provide information based on available school data
- Stay focused on school-related topics
- No PREAMBLE or unnecessary information
- Politely redirect off-topic questions to school matters
- Respond "I apologize, but I can only provide information about school-related matters" for non-school topics
Context for responses: {context}"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

# #creating RAG chain
# def get_rag_chain(model="llama8b"):
#     llm = ChatGroq(model=model)
#     history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
#     question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
#     rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)    
#     return rag_chain



import logging  # Add this import

def get_rag_chain(model="gemma2-9b-it"):  # Updated default model name
    # Validate model name with correct Groq model identifiers
    valid_models = [
        "gemma2-9b-it",    # Default model
        "llama-3.1-8b-instant",      # Alternative model
    ]
    
    if model not in valid_models:
        logging.warning(f"Invalid model {model}, using default model")
        model = "gemma2-9b-it"
    
    try:
        llm = ChatGroq(model=model)
        history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
        return rag_chain
    except Exception as e:
        logging.error(f"Error creating RAG chain: {str(e)}")
        raise