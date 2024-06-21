# Import necessary libraries
import os
import streamlit as st
import pickle
import time
from langchain import OpenAI
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import UnstructuredURLLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

from dotenv import load_dotenv
load_dotenv()  # Take environment variables from .env (especially OpenAI API key)

# Set the title of the Streamlit app
st.title("News Research Tool 📈")

# Define the sidebar title
st.sidebar.title("News Article URLs")

# Define a list to store the URLs
urls = []

# Loop through the range of 3 to get 3 URLs
for i in range(3):
    # Get the URL input from the user and append it to the list
    url = st.sidebar.text_input(f"URL {i+1}")
    urls.append(url)

# Define a button for the user to click to process the URLs
process_url_clicked = st.sidebar.button("Process URLs")

# Define the file path for the FAISS store
file_path = "faiss_store_openai.pkl"

# Create an empty placeholder for the main Streamlit app
main_placeholder = st.empty()

# Initialize the OpenAI language model
llm = OpenAI(temperature=0.9, max_tokens=500)

# Check if the user has clicked the process URLs button
if process_url_clicked:
    # Load the data from the URLs
    loader = UnstructuredURLLoader(urls=urls)
    main_placeholder.text("Data Loading...Started...")
    data = loader.load()

    # Split the data into documents
    text_splitter = RecursiveCharacterTextSplitter(
        separators=['\n\n', '\n', '.', ','],
        chunk_size=1000
    )
    main_placeholder.text("Text Splitter...Started...")
    docs = text_splitter.split_documents(data)

    # Create embeddings for the documents
    embeddings = OpenAIEmbeddings()
    vectorstore_openai = FAISS.from_documents(docs, embeddings)
    main_placeholder.text("Embedding Vector Started Building...")
    time.sleep(2)

    # Save the vectorstore to a file
    with open(file_path, "wb") as f:
        pickle.dump(vectorstore_openai, f)

# Get the search query from the user
query=main_placeholder.text_input("Search Query")

# Check if there is a search query and if the FAISS store file exists
if query and os.path.exists(file_path):
    # Load the FAISS store from the file
    with open(file_path, "rb") as f:
        vectorstore = pickle.load(f)

        # Create a RetrievalQAWithSourcesChain using the language model and the vectorstore as a retriever
        chain= RetrievalQAWithSourcesChain.from_chain_type(llm=llm,  
        retriever=vectorstore.as_retriever())

        # Run the chain with the search query
        result = chain({"question": query}, return_only_outputs=True)

        # Display the results
        st.header("Results")
        st.write(result["answer"])
        sources = result.get("sources", "")
        if sources:
            st.subheader("Sources:")
            sources_list = sources.split("\n")  # Split the sources by newline
            for source in sources_list:
                st.write(source)
   

