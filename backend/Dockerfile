FROM python:3.8-slim
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir
COPY . .

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]

LABEL author='roman.petrakov@gmail.com' version=1.0.0 app_name=foodgram