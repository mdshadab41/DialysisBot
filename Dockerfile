FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

COPY . .

RUN mkdir -p /data/docs /data/chroma_db

RUN mkdir -p /root/.streamlit && echo '\
[server]\n\
headless = true\n\
port = 7860\n\
address = "0.0.0.0"\n\
enableCORS = false\n\
enableXsrfProtection = false\n\
' > /root/.streamlit/config.toml

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:7860/_stcore/health || exit 1

CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]