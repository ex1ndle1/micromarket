FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /code

COPY pyproject.toml uv.lock ./

RUN uv pip install --system --no-cache-dir .

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "&&" , "celery" , "-A" , "app.currency" , "worker" , "--loglevel=INFO" , "-B" ]
