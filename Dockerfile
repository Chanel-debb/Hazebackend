FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=0
ENV UV_LINK_MODE=copy
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev


COPY . /app


ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT []
EXPOSE 8080

CMD ["gunicorn", "main.wsgi:application", "--bind", "0.0.0.0:8080"]



# create a .dockerignore and list the virtualenv and __pycache__/
# docker build -t appname .
# docker run -d --name hazebackend_container -p 8000:8000 hazebackend
# docker ps
# docker logs -f hazebackend_container