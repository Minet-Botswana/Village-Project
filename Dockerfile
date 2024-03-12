FROM python:3.11.5
RUN mkdir /code
WORKDIR /code
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:80", "insurancemanagement.wsgi"]