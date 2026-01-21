## About

**RAG Multimodel App** is a backend application that implements a **Retrieval-Augmented Generation (RAG)** pipeline for multiple file formats.
It allows ingesting documents, converting them into vector embeddings, storing them in a vector database, and performing fast semantic search powered by Large Language Models (LLMs).

### Key Features

* Supports multiple document formats (PDF, TXT, DOCX, etc.)
* RAG (Retrieval-Augmented Generation) workflow
* Vector database storage for efficient similarity search
* Fast and scalable semantic search
* LLM-powered question answering over indexed documents
* Docker-ready for easy deployment
* Can run locally using a Python virtual environment

### Use Cases

* Document-based Q&A systems
* Knowledge base search
* AI assistants over private documents
* Enterprise search and retrieval systems

The project is designed to be modular, extensible, and production-ready, making it suitable for experimentation as well as real-world applications.


## INSTALLATION

---

## Option 1: Installation using Docker

### Prerequisites

* Docker
* `.env` file (if required)

### Build Docker image

sudo docker build -t rag_multimodel:latest .

### Remove existing container (if any)

sudo docker rm -f rag_multimodel

### Run Docker container

sudo docker run -d 
-p 3001:3000 
-v $(pwd)/chroma_db:/app/chroma_db 
--env-file .env 
--name rag_multimodel 
rag_multimodel:latest

### Check running containers

sudo docker ps

### View logs

sudo docker logs rag_multimodel

### Stop container

sudo docker stop rag_multimodel

### Application URL

[http://localhost:3001](http://localhost:3001)

---

## Option 2: Installation using Local Environment (Direct Run)

### Create virtual environment

python -m venv venv

### Activate virtual environment (Windows)

.\venv\Scripts\Activate.ps1

### Activate virtual environment (Mac / Linux)

source venv/bin/activate

### Install / update dependencies

pip install -r requirements.txt

### Run the project

uvicorn app.main:app --reload
