FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
COPY enhanced_agent enhanced_agent/
COPY enhanced_agent_streamlit.py .
COPY config config/
COPY .streamlit .streamlit/

RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -e enhanced_agent/

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

CMD ["streamlit", "run", "enhanced_agent_streamlit.py", "--server.port=8501", "--server.address=0.0.0.0"]
