import streamlit as st
from api_utils import upload_document, list_documents, delete_document

# def display_sidebar():
#     # Model selection
#     model_options = ["llama-3.1-8b-instant","gemma"]
#     st.sidebar.selectbox("Select Model", options=model_options, key="model")

#     # Document upload
#     uploaded_file = st.sidebar.file_uploader("Choose a file", type=["pdf", "docx", "html"])
#     if uploaded_file and st.sidebar.button("Upload"):
#         with st.spinner("Uploading..."):
#             upload_response = upload_document(uploaded_file)
#             if upload_response:
#                 st.sidebar.success(f"File uploaded successfully with ID {upload_response['file_id']}.")
#                 st.session_state.documents = list_documents()


def display_sidebar():
    # Model selection with correct model identifiers
    model_mapping = {
        "LLaMA 3.1": "llama-3.1-8b-instant",
        "Gemma": "gemma2-9b-it"
    }
    
    selected_model_name = st.sidebar.selectbox(
        "Select Model",
        options=list(model_mapping.keys()),
        key="model_name"
    )
    
    # Store the actual model identifier in session state
    st.session_state.model = model_mapping[selected_model_name]
    
    # Show current model
    st.sidebar.caption(f"Using model: {st.session_state.model}")

    # Document upload section
    st.sidebar.header("Document Management")
    uploaded_file = st.sidebar.file_uploader("Choose a file", type=["pdf", "docx", "html"])
    # ...existing code...



    # List and delete documents
    st.sidebar.header("Uploaded Documents")
    if st.sidebar.button("Refresh Document List"):
        st.session_state.documents = list_documents()

    # Display document list and delete functionality
    if "documents" in st.session_state and st.session_state.documents:
        for doc in st.session_state.documents:
            st.sidebar.text(f"{doc['filename']} (ID: {doc['id']})")

        selected_file_id = st.sidebar.selectbox("Select a document to delete", 
                                                options=[doc['id'] for doc in st.session_state.documents])
        if st.sidebar.button("Delete Selected Document"):
            delete_response = delete_document(selected_file_id)
            if delete_response:
                st.sidebar.success(f"Document deleted successfully.")
                st.session_state.documents = list_documents()
