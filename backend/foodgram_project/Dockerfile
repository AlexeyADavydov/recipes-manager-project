FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

CMD ["gunicorn", "foodgram_project.wsgi:application", "--bind", "0.0.0.0:8000"]
