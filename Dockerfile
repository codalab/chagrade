FROM python:3.7
ENV PYTHONUNBUFFERED 1

# Install the gunicorn server to serve django
#RUN pip install gunicorn==19.6.0

# Install the dependencies (rarely change)
ADD requirements.txt .
RUN pip install -r requirements.txt

## Install the app code (change often)
#ADD . /app

WORKDIR /app
CMD ["/usr/local/bin/gunicorn", "chagrade.wsgi:application", "-w 2", "--timeout=300", "-b :8000"]
