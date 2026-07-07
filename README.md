---
title: DialysisBot
emoji: 🏥
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# 🏥 DialysisBot — AI-Powered Clinical RAG Chatbot

[![Live Demo](https://img.shields.io/badge/Live%20Demo-HuggingFace%20Spaces-blue?style=for-the-badge&logo=huggingface)](https://shadab-41-dialysisbot.hf.space)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?style=for-the-badge&logo=github)](https://github.com/mdshadab41/DialysisBot)
[![Docker Hub](https://img.shields.io/badge/Docker%20Hub-mdshadab41%2Fdialysisbot-blue?style=for-the-badge&logo=docker)](https://hub.docker.com/r/mdshadab41/dialysisbot)
[![Python](https://img.shields.io/badge/Python-3.11-green?style=for-the-badge&logo=python)](https://python.org)

> A production-grade RAG chatbot for dialysis patients built with Python, Streamlit, Groq, and ChromaDB. Fully containerized with Docker and deployed via Jenkins CI/CD pipeline on AWS EC2.

---

## 🌐 Live Demo

👉 **[https://shadab-41-dialysisbot.hf.space](https://shadab-41-dialysisbot.hf.space)**

---

## ✨ Features

- **RAG Pipeline** — PDF ingestion → chunking → embeddings → vector search → LLM response
- **DeepEval Evaluation** — 4 metrics across 25 clinical questions
- **RAG vs Non-RAG Comparison** — Side-by-side comparison mode
- **Confidence Scoring** — Real-time confidence scores for every answer
- **Modern UI** — Gradient dark theme with clean chat interface
- **PDF Management** — Upload and manage knowledge base documents
- **CI/CD Pipeline** — Fully automated Jenkins pipeline (48 seconds)

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|-----------|
| Language | Python 3.11 |
| UI | Streamlit |
| LLM | Groq API (Llama 3.1 8B) |
| Embeddings | Sentence Transformers (all-MiniLM-L6-v2) |
| Vector DB | ChromaDB |
| Evaluation | DeepEval |
| Container | Docker (multi-stage build) |
| CI/CD | Jenkins (AWS EC2) |
| Registry | AWS ECR |
| Deployment | HuggingFace Spaces |
| Version Control | Git + GitHub |

---

## 📊 Key Metrics

| Metric | Value |
|--------|-------|
| Pipeline Duration | 48 seconds |
| Build Context Reduction | 2.8GB → 17MB (165x) |
| Evaluation Questions | 25 clinical questions |
| Document Chunks | 200 chunks from 6 PDFs |
| Embedding Dimensions | 384 |
| Production Issues Resolved | 12 |
| Pipeline Stages | 7 |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker Desktop
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Local Setup

```bash
# Clone repository
git clone https://github.com/mdshadab41/DialysisBot.git
cd DialysisBot

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "GROQ_API_KEY=your_key_here" > .env

# Build vector database
python vector_store.py

# Run app
streamlit run app.py
```

### Docker Setup

```bash
# Build and run
docker compose up
```

Open: **http://localhost:8501**

---

## 📁 Project Structure

```
DialysisBot/
├── app.py                  # Streamlit UI
├── chat.py                 # RAG chat module
├── retriever.py            # Vector search
├── embeddings.py           # Sentence transformers
├── vector_store.py         # ChromaDB management
├── pdf_loader.py           # PDF processing
├── pdf_manager.py          # PDF upload/delete
├── text_splitter.py        # Document chunking
├── confidence.py           # Confidence scoring
├── comparison.py           # RAG vs Non-RAG
├── evaluation.py           # DeepEval evaluation
├── config.py               # Configuration
├── requirements.txt        # Dependencies
├── Dockerfile              # Multi-stage build
├── docker-compose.yml      # Local development
├── Jenkinsfile             # CI/CD pipeline
├── .env.example            # Environment template
└── docs/                   # PDF knowledge base
```

---

## 🔄 CI/CD Pipeline

Jenkins pipeline runs automatically on every GitHub push via webhook:

1. **Checkout** — Pull latest code from GitHub
2. **Verify Files** — Confirm project structure
3. **Build Docker** — Multi-stage image build
4. **Test Container** — Start/stop container test
5. **Push to ECR** — Publish to AWS ECR
6. **Deploy HuggingFace** — Push to HF Spaces
7. **Cleanup** — Remove old images

**Total pipeline time: ~48 seconds**

---

## 🧪 Evaluation

Run DeepEval evaluation:

```bash
python evaluation.py
```

Metrics evaluated:
- **Faithfulness** — Does answer stick to documents?
- **Answer Relevancy** — Does answer address the question?
- **Contextual Precision** — Are top chunks most relevant?
- **Contextual Recall** — Did retrieval cover everything needed?

---

## 🔧 Jenkins Credentials Required

```
groq-api-key      → Groq API key
hf-token          → HuggingFace token
aws-access-key    → AWS Access Key ID
aws-secret-key    → AWS Secret Access Key
```

---

## 🐛 Production Issues Resolved

1. Ollama incompatible with cloud → switched to Groq API
2. ChromaDB dimension mismatch (768→384) → full rebuild
3. Docker build context 2.8GB → 17MB via .dockerignore
4. Groq model deprecation → updated to llama-3.1-8b-instant
5. ChromaDB tenant connection error → updated client syntax
6. HuggingFace binary file rejection → Git LFS
7. Port mismatch (8501 vs 7860) → updated Dockerfile
8. PDF persistence loss → prebuilt ChromaDB in Dockerfile
9. Streamlit upload 400 errors → pushed PDFs via git
10. Groq connection errors → switched to requests.post()
11. API key newline character → added .strip()
12. Docker socket permissions → chmod 666 in Jenkins

---

## 📝 Environment Variables

```bash
# Copy .env.example to .env
cp .env.example .env

# Required
GROQ_API_KEY=your_groq_api_key_here
```

---

## 🔗 Project Links

- 🚀 Live App: [https://shadab-41-dialysisbot.hf.space](https://shadab-41-dialysisbot.hf.space)
- 📦 GitHub: [https://github.com/mdshadab41/DialysisBot](https://github.com/mdshadab41/DialysisBot)
- 🐳 Docker Hub: [https://hub.docker.com/r/mdshadab41/dialysisbot](https://hub.docker.com/r/mdshadab41/dialysisbot)
- 🤗 HuggingFace: [https://huggingface.co/spaces/shadab-41/DialysisBot](https://huggingface.co/spaces/shadab-41/DialysisBot)

---

## 🤝 Connect With Me

- 🌐 GitHub: [https://github.com/mdshadab41](https://github.com/mdshadab41)
- 💼 LinkedIn: [https://www.linkedin.com/in/md-shadab-a52981130](https://www.linkedin.com/in/md-shadab-a52981130)

---

## ⚠️ Medical Disclaimer

This chatbot is for educational and informational purposes only. It is NOT a substitute for professional medical advice, diagnosis, or treatment. Always consult your doctor or healthcare provider for medical decisions.