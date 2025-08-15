FROM ghcr.io/astral-sh/uv:alpine

WORKDIR /app

# Install PostgreSQL client and build dependencies
RUN apk add --no-cache postgresql-client gcc python3-dev musl-dev linux-headers

# Copy project files
COPY . .

# Install project dependencies using uv
RUN uv sync

# Use uv to run the application
CMD ["uv", "run", "-m", "app.presentation.telegram"]
