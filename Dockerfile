FROM python:3.7.1
RUN mkdir /app
WORKDIR /app
ADD . .
RUN apt-get update && apt-get install -y python-dev libldap2-dev libsasl2-dev libssl-dev
RUN pip install -r requirements.txt
EXPOSE 5010
WORKDIR /app/src
CMD ["bash", "run.sh"]
