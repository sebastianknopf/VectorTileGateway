FROM python:3.12-slim

RUN apt update -y && apt install -y git

WORKDIR /app

COPY .git/ /app/.git
RUN mkdir -p /app/src/

COPY pyproject.toml /app
RUN pip install --no-cache-dir .

COPY src/ /app/src
RUN pip install --no-deps .

COPY resources/ /app/resources

EXPOSE 8080

ENTRYPOINT ["python"]
CMD ["-m", "uvicorn", "src.api:app", "--port", "8080", "--proxy-headers", "--forwarded-allow-ips=*", "--host", "0.0.0.0"]