FROM python:3.11

# set environment vars
ENV PYTHONUNBUFFERED True
ENV APP_HOME /root
ENV POETRY_VERSION=1.6.1
ENV POETRY_HOME="/opt/poetry"
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV POETRY_NO_INTERACTION=1
ENV PATH="$POETRY_HOME/bin:$PATH"

# install poetry
RUN /bin/bash -c "set -o pipefail && curl -sSL https://install.python-poetry.org | python"

# set working directory
WORKDIR $APP_HOME

# copy project files
COPY /webhook_handler $APP_HOME/webhook_handler
COPY poetry.lock pyproject.toml $APP_HOME/

# install
RUN poetry install --no-root

EXPOSE 8080
CMD ["poetry", "run", "uvicorn", "webhook_handler.main:app", "--host", "0.0.0.0", "--port", "8080"]
