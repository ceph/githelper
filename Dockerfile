FROM docker.io/library/python:alpine
ENV REPOBASE="/git"
RUN \
  apk add --no-cache bash git tini && \
  mkdir -p /opt/githelper /git
COPY . /opt/githelper
RUN \
  cd /opt/githelper && \
  python3 -m venv venv && \
  source ./venv/bin/activate && \
  pip3 install -e . && \
  pip3 install gunicorn
EXPOSE 8080
ENTRYPOINT /opt/githelper/entrypoint.sh
