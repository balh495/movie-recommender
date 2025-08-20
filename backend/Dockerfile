FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl git build-essential \
    && rm -rf /var/lib/apt/lists/*

# Installation of Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

ENV PATH="/root/.ollama/bin:$PATH"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose Streamlit port
EXPOSE 8501

# Start Ollama and Streamlit
CMD ollama serve & sleep 3 && ollama pull nomic-embed-text:latest && streamlit run app.py