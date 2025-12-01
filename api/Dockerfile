FROM python:3.12-slim

WORKDIR /app/api

COPY ./requirements.txt .

EXPOSE 8000

COPY . ./api

RUN pip install -r requirements.txt

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]