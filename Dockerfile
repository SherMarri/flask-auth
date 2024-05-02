FROM python:3.9

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY . /app

# Run flask app using `wsgi` server
CMD ["gunicorn", "-b", "0.0.0.0:5000", "wsgi:app"]