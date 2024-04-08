#############################################
# currency explorer PROD container #
#############################################
FROM tiangolo/uvicorn-gunicorn:python3.11-slim

WORKDIR /src
COPY ${PWD}/pyproject.toml ./pyproject.toml
COPY ./ /src

RUN pip install --upgrade pip
RUN pip install poetry==1.4.2
RUN poetry config virtualenvs.create false
RUN poetry install --without dev --no-root

ARG ENVIRONMENT="PROD"
ARG PORT

ENV PYTHONPATH "${PYTHONPATH}:/src"
ENV ENVIRONMENT="PROD"

EXPOSE ${PORT}


CMD ["uvicorn", "currencyexplorer.main:app", "--host", "0.0.0.0", "--port", "echo ${PORT}"]