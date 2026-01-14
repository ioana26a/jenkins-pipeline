FROM python:3.7-alpine

RUN apk add --no-cache nginx nano curl bash python3 py3-pip

RUN pip3 install flask flask-cors mysql-connector-python

COPY default.conf /etc/nginx/http.d/default.conf
COPY index.html /var/lib/nginx/html/index.html
COPY app.py /app/app.py
COPY init_db.py /app/init_db.py

WORKDIR /app

EXPOSE 80 5000
CMD sh -c "python3 app.py & nginx -g 'daemon off;'"
