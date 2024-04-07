#############################################
# currency explorer DEV container #
#############################################
FROM tiangolo/uvicorn-gunicorn:python3.11-slim


COPY ${PWD}/pyproject.toml ./pyproject.toml
ENV PYTHONPATH "${PYTHONPATH}:/app"
ENV ENVIRONMENT="DEV"
ENV PORT=8002


RUN pip install --upgrade pip
RUN pip install poetry==1.4.2

RUN poetry config virtualenvs.create false
RUN poetry install
#RUN pip install --force-reinstall  email-validator==2.0.0