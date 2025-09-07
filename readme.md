"𝐃𝐨𝐜𝐛𝐨𝐭" , a Digital Health Assistant designed to help patients and healthcare professionals access accurate, timely medical information with ease.

𝐂𝐨𝐫𝐞:
- Provides reliable, context-aware responses to complex medical queries, from symptom checks to treatment advice.

- The chatbot tailors responses based on the patient’s input, offering context-aware advice that feels personalized and relevant to their specific situation.

- Combines Retrieval-Augmented Generation (RAG) with Llama3 and GPT-4 LLMs for precision and fluency. Using the RAG technique, the chatbot accesses accurate and highly relevant information about medical conditions and potential solutions by integrating an external knowledge base where the medical data is stored.

The Rag solution grounded with The GALE ENCYCLOPEDIA of MEDICINE: http://bit.ly/43w9RmV

This repo is a FastAPI app that serves as an interface for retrieving information from the knowledge base and giving most relevant information to the user. It makes the reponses conversational and answers follow up question for a dynamic conversational flow between the user and the chatbot.

Architecture:
<img width="1280" height="1007" alt="image" src="https://github.com/user-attachments/assets/d57c8194-47d0-49ab-9a14-ae67809a9341" />
