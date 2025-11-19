# 🏛️ JurisGPT — AI-Powered Indian Law Information System

JurisGPT is an AI-driven legal information platform designed to answer queries about
Indian laws such as:
- Constitution of India
- Bharatiya Nyaya Sanhita (BNS)
- Indian Penal Code (IPC)
- Case laws and legal references

This project uses **RAG (Retrieval Augmented Generation)** with:
- Next.js (TypeScript) — Frontend
- FastAPI (Python) — Backend
- MongoDB — Structured storage
- FAISS — Vector search for embeddings
- Llama 3 — AI answer generation

This repository is a **monorepo** containing both frontend and backend code.

---

## 📁 Project Structure

jurisgpt/
│
├── frontend/ → Next.js 14 + TypeScript app
├── backend/ → FastAPI server with RAG pipeline
├── data/ → Raw legal texts
├── embeddings/ → FAISS index and vector files
├── models/ → ML models (optional)
├── docs/ → SRS, SPMP, diagrams
└── README.md


---

## 🛠️ Tech Stack

### Frontend
- Next.js 14
- TypeScript
- TailwindCSS / Material UI
- Axios (API calls)

### Backend
- FastAPI
- LangChain / LlamaIndex
- FAISS
- PyPDF / text preprocessing tools

### Database
- MongoDB (Atlas or local)

---

## 🚀 Features (as per SRS)

### User Side
- Submit legal queries
- Receive verified + sourced AI answers
- View history
- Bookmark responses
- Multilingual support (English + Indian languages)

### Admin Side
- Upload legal documents
- Run preprocessing + embeddings
- Manage versions
- Inspect flagged responses
- Monitor analytics

---

## 📌 Status
Project currently in **Phase M0: Initialization**  
Next step: Set up frontend and backend scaffolding.


