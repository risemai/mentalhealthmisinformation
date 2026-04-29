FROM python:3.11-slim

# ── system deps 
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# ── HuggingFace Spaces convention: run as non-root user 
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR /app

# ── install Python deps 
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── copy project files 
COPY --chown=user . .

# ── expose port 
EXPOSE 7860

# ── Streamlit config for HF Spaces 
ENV STREAMLIT_SERVER_PORT=7860 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_THEME_BASE=light \
    STREAMLIT_THEME_BACKGROUND_COLOR="#F8F9FA" \
    STREAMLIT_THEME_TEXT_COLOR="#212529" \
    STREAMLIT_THEME_PRIMARY_COLOR="#10B981"

CMD ["streamlit", "run", "app.py", \
    "--server.port=7860", \
    "--server.address=0.0.0.0", \
    "--server.headless=true", \
    "--browser.gatherUsageStats=false"]
