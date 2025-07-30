FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install uv for dependency management
RUN pip install --no-cache-dir uv

# Copy project files
COPY . .

# Install project dependencies using uv
RUN uv pip install --system .

CMD ["python3", "-m", "app.presentation.telegram"]
