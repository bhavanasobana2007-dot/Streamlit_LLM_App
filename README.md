# Week 14 - Streamlit LLM Application

## Task Title
Developing an Interactive LLM Web Application
using Streamlit and Ollama.

## Domain
Education

## Objective
- Create an interactive LLM web application.
- Upload PDF documents.
- Ask questions about PDF documents.
- Retrieve relevant information using ChromaDB.
- Generate answers using Ollama.

## Technologies Used
- Python
- Streamlit
- LangChain
- ChromaDB
- Sentence Transformers
- Ollama
- PyPDF
- Pandas

## Models
Embedding Model: all-MiniLM-L6-v2

LLM Model: llama3.2:3b

## Features
1. PDF Upload
2. Multiple PDF Selection
3. PDF Validation
4. AI Question Answering
5. Semantic Search
6. Chat History
7. Clear Chat History
8. Retrieved Document Sections
9. Response Generation Time
10. CSV Output

## Implementation
1. Created Streamlit application.
2. Uploaded PDF documents.
3. Extracted PDF text.
4. Split text into chunks.
5. Generated embeddings.
6. Stored embeddings in ChromaDB.
7. Retrieved relevant chunks.
8. Generated answers using Ollama.
9. Displayed answers in Streamlit.
10. Saved questions and answers in CSV.

## Output Files
- queries.csv
- answers.csv

## Conclusion
The Streamlit LLM application was developed
using LangChain, ChromaDB, and Ollama.

The application allows users to upload PDF
documents and ask questions through an
interactive web interface.