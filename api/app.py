# from fastapi import FastAPI, File, UploadFile, HTTPException
# from pydantic_models import QueryInput, QueryResponse, DocumentInfo, DeleteFileRequest
# from langchain_utils import get_rag_chain
# from db_utils import insert_application_logs, get_chat_history, get_all_documents, insert_document_record, delete_document_record
# from chroma_utils import index_document_to_chroma, delete_doc_from_chroma
# import os
# import uuid
# import logging
# import shutil
# from fastapi.middleware.cors import CORSMiddleware

# # Set up logging
# logging.basicConfig(filename='app.log', level=logging.INFO)

# # Configure logging
# logging.basicConfig(
#     filename='app.log',
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )

# # Initialize FastAPI app
# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Allows all origins
#     allow_credentials=True,
#     allow_methods=["*"],  # Allows all methods
#     allow_headers=["*"],  # Allows all headers
# )


# #chat endpoint
# @app.post("/chat", response_model=QueryResponse)
# def chat(query_input: QueryInput):
#     session_id = query_input.session_id or str(uuid.uuid4())
#     logging.info(f"Session ID: {session_id}, User Query: {query_input.question}, Model: {query_input.model.value}")

#     chat_history = get_chat_history(session_id)
#     rag_chain = get_rag_chain(query_input.model.value)
#     answer = rag_chain.invoke({
#         "input": query_input.question,
#         "chat_history": chat_history
#     })['answer']

#     insert_application_logs(session_id, query_input.question, answer, query_input.model.value)
#     logging.info(f"Session ID: {session_id}, AI Response: {answer}")
#     return QueryResponse(answer=answer, session_id=session_id, model=query_input.model)


# #document upload endpoint
# @app.post("/upload-doc")
# def upload_and_index_document(file: UploadFile = File(...)):
#     allowed_extensions = ['.pdf', '.docx', '.html']
#     file_extension = os.path.splitext(file.filename)[1].lower()

#     if file_extension not in allowed_extensions:
#         raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed types are: {', '.join(allowed_extensions)}")

#     temp_file_path = f"temp_{file.filename}"

#     try:
#         # Save the uploaded file to a temporary file
#         with open(temp_file_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)

#         file_id = insert_document_record(file.filename)
#         success = index_document_to_chroma(temp_file_path, file_id)

#         if success:
#             return {"message": f"File {file.filename} has been successfully uploaded and indexed.", "file_id": file_id}
#         else:
#             delete_document_record(file_id)
#             raise HTTPException(status_code=500, detail=f"Failed to index {file.filename}.")
#     finally:
#         if os.path.exists(temp_file_path):
#             os.remove(temp_file_path)

# #list endpoint
# @app.get("/list-docs", response_model=list[DocumentInfo])
# def list_documents():
#     return get_all_documents()



# #delete endpoint
# @app.post("/delete-doc")
# def delete_document(request: DeleteFileRequest):
#     chroma_delete_success = delete_doc_from_chroma(request.file_id)

#     if chroma_delete_success:
#         db_delete_success = delete_document_record(request.file_id)
#         if db_delete_success:
#             return {"message": f"Successfully deleted document with file_id {request.file_id} from the system."}
#         else:
#             return {"error": f"Deleted from Chroma but failed to delete document with file_id {request.file_id} from the database."}
#     else:
#         return {"error": f"Failed to delete document with file_id {request.file_id} from Chroma."}

# # ...existing code...

# # Add this at the bottom of the file
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8080, log_level="info")






from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pydantic import ValidationError
from pydantic_models import QueryInput, QueryResponse, DocumentInfo, DeleteFileRequest
from langchain_utils import get_rag_chain
from db_utils import (
    insert_application_logs,
    get_chat_history,
    get_all_documents,
    insert_document_record,
    delete_document_record
)
from chroma_utils import index_document_to_chroma, delete_doc_from_chroma
import os
import uuid
import logging
import shutil

app = Flask(__name__)
CORS(app)  # Enable CORS for development

# Configure logging
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Serve HTML template
@app.route('/')
def home():
    return render_template('home.html')

# Chat Endpoint
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        query_input = QueryInput(**data)  # Validate with Pydantic
        
        session_id = query_input.session_id or str(uuid.uuid4())
        logging.info(
            f"Session ID: {session_id}, User Query: {query_input.question}, Model: {query_input.model.value}"
        )

        chat_history = get_chat_history(session_id)
        rag_chain = get_rag_chain(query_input.model.value)
        answer = rag_chain.invoke({
            "input": query_input.question,
            "chat_history": chat_history
        })['answer']

        insert_application_logs(
            session_id,
            query_input.question,
            answer,
            query_input.model.value
        )

        response = QueryResponse(
            answer=answer,
            session_id=session_id,
            model=query_input.model.value
        ).dict()

        return jsonify(response), 200

    except ValidationError as ve:
        return jsonify({"error": "Invalid request data"}), 400
    except Exception as e:
        logging.error(str(e))
        return jsonify({"error": "Internal server error"}), 500

# File Upload Endpoint
@app.route('/upload-doc', methods=['POST'])
def upload_and_index_document():
    try:
        file = request.files['file']
        allowed_extensions = {".pdf", ".docx", ".html", ".txt"}
        _, file_ext = os.path.splitext(file.filename)
        
        if file_ext.lower() not in allowed_extensions:
            return jsonify({"error": "Unsupported file type"}), 400

        temp_file_path = f"/tmp/{uuid.uuid4()}_{file.filename}"
        file.save(temp_file_path)

        file_id = insert_document_record(file.filename)
        success = index_document_to_chroma(temp_file_path, file_id)

        if success:
            return jsonify({
                "message": "File uploaded",
                "file_id": file_id
            }), 200
        else:
            delete_document_record(file_id)
            return jsonify({"error": "Failed to index file"}), 500

    except Exception as e:
        logging.error(str(e))
        return jsonify({"error": "Upload failed"}), 500

# Document List Endpoint
@app.route('/list-docs', methods=['GET'])
def list_documents():
    try:
        documents = get_all_documents()
        return jsonify([doc.dict() for doc in documents]), 200  # Assuming DocumentInfo has .dict()
    except Exception as e:
        logging.error(str(e))
        return jsonify({"error": "Failed to list documents"}), 500

# Document Deletion Endpoint
@app.route('/delete-doc', methods=['POST'])
def delete_document():
    try:
        data = request.get_json()
        file_id = data.get('file_id')
        
        if not file_id:
            return jsonify({"error": "Missing file_id"}), 400

        chroma_success = delete_doc_from_chroma(file_id)
        db_success = delete_document_record(file_id)

        if chroma_success and db_success:
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "partial success"}), 200

    except Exception as e:
        logging.error(str(e))
        return jsonify({"error": "Deletion failed"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)








