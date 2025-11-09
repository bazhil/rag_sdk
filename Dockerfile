FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    fonts-dejavu-core \
    fonts-dejavu-extra \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN if [ ! -f "llm_manager/requirements.txt" ]; then \
        echo "ERROR: llm_manager submodule not initialized!"; \
        echo "Please run: git submodule update --init --recursive"; \
        exit 1; \
    fi

RUN pip install --no-cache-dir -r llm_manager/requirements.txt

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

