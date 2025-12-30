# Domain-RAG-Chatbot-Film-Trivia-Assistant
Film Trivia RAG Chatbot — A retrieval-augmented AI chatbot that answers film trivia using vector search over curated movie documents, providing citation-backed responses via a FastAPI backend and Next.js frontend.


## Environment Setup

```bash
conda create -n film-rag python=3.10
conda activate film-rag
pip install -r requirements.txt


# Domain RAG Chatbot — Film Trivia Assistant

## Overview
A retrieval-augmented chatbot that answers film trivia using a curated corpus
(IMDb plot summaries, director interviews, film articles), with source citations.

## Problem Statement
LLMs hallucinate on niche film trivia. This project grounds answers in retrieved
documents to improve factual accuracy and transparency.

## Architecture (High-level)
- Document ingestion & chunking
- Vector embedding + similarity search
- Prompt-augmented generation
- Source citation in responses

## Tech Stack
- Python
- Sentence-Transformers (embeddings)
- FAISS(vector store)
- FastAPI (backend)
- Next.js (frontend)
- Docker

## Data Sources (Planned)
- IMDb plot summaries
- Wikipedia film articles
- Director interviews (public sources)

## Features (Planned)
- Document ingestion pipeline
- Semantic search over film corpus
- RAG-based answer generation
- Source citation snippets
- Conversation history per session

## Evaluation
- Retrieval Precision@K
- Manual hallucination checks
- User correctness study


Embedding: sentence-transformers/all-MiniLM-L6-v2
Vector DB: FAISS
Generator: google/flan-t5-base
Backend: FastAPI
Frontend:  Next.js

#Embeddings
- Model: all-MiniLM-L6-v2
- Batch embedding pipeline
- Vectors persisted as NumPy arrays
- Metadata stored separately for retrieval and citation