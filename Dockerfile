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

# Create .streamlit directory and config for production
RUN mkdir -p .streamlit && \
    echo '[server]' > .streamlit/config.toml && \
    echo 'port = 8501' >> .streamlit/config.toml && \
    echo 'address = "0.0.0.0"' >> .streamlit/config.toml && \
    echo 'headless = true' >> .streamlit/config.toml && \
    echo 'enableCORS = false' >> .streamlit/config.toml && \
    echo 'enableXsrfProtection = true' >> .streamlit/config.toml && \
    echo '' >> .streamlit/config.toml && \
    echo '[browser]' >> .streamlit/config.toml && \
    echo 'gatherUsageStats = false' >> .streamlit/config.toml && \
    echo 'serverAddress = "0.0.0.0"' >> .streamlit/config.toml && \
    echo 'serverPort = 8501' >> .streamlit/config.toml && \
    echo '' >> .streamlit/config.toml && \
    echo '[theme]' >> .streamlit/config.toml && \
    echo 'base = "light"' >> .streamlit/config.toml && \
    echo 'primaryColor = "#FF4B4B"' >> .streamlit/config.toml && \
    echo 'backgroundColor = "#FFFFFF"' >> .streamlit/config.toml && \
    echo 'secondaryBackgroundColor = "#F0F2F6"' >> .streamlit/config.toml && \
    echo 'textColor = "#262730"' >> .streamlit/config.toml && \
    echo '' >> .streamlit/config.toml && \
    echo '[client]' >> .streamlit/config.toml && \
    echo 'showErrorDetails = false' >> .streamlit/config.toml && \
    echo 'toolbarMode = "minimal"' >> .streamlit/config.toml

RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir git+https://github.com/mannaandpoem/OpenManus.git && \
    pip install --no-cache-dir -e enhanced_agent/

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

CMD ["streamlit", "run", "enhanced_agent_streamlit.py", "--server.port=8501", "--server.address=0.0.0.0"]
