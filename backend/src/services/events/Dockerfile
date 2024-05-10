FROM python:3.12-slim-bookworm

COPY requirements.txt events/requirements.txt
WORKDIR /events
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000" ,"--reload"]