FROM python:3.6-alpine

# Environment Variables
ENV FLASK_APP=microblog.py
ENV FLASK_ENVIRONMENT=production
ENV FLASK_RUN_PORT=5000
# Don't copy .pyc files to cointainer
ENV PYTHONDONTWRITEBYTECODE=1

# Security / Permissions (1/2)
RUN adduser -D microblog
WORKDIR /home/microblog

# Virtual Environment
COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -U pip
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn pymysql

# Install App
COPY app app
COPY migrations migrations
COPY microblog.py config.py boot.sh ./
RUN chmod +x boot.sh

# Security / Permissions (2/2)
RUN chown -R microblog:microblog ./
USER microblog

# Start Application
EXPOSE 5000/tcp
ENTRYPOINT ["./boot.sh"]