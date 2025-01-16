# Stage 1: Build environment
FROM python:3.13-alpine AS builder

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Production-ready image
FROM python:3.13-alpine

# Set the working directory
WORKDIR /app

# Copy only the installed dependencies from the builder stage
COPY --from=builder /install /usr/local

COPY ./app ./app
COPY ./alembic.ini .
COPY ./alembic/env.py ./alembic/env.py
COPY ./alembic/script.py.mako ./alembic/script.py.mako

RUN mkdir -p /app/alembic/versions && alembic revision --autogenerate -m "Initial migration" && alembic upgrade head

# RUN addgroup -S noroot && adduser -S noroot -G noroot

# RUN chown -R noroot:noroot /app

# USER noroot

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]