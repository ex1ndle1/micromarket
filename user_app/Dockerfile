FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /code

COPY pyproject.toml uv.lock ./

RUN uv pip install --system --no-cache-dir .

COPY ./user_app /code/user_app

CMD ["uvicorn", "user_app.main:app", "--host", "0.0.0.0", "--port", "8001"]
