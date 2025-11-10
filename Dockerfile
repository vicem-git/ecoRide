# FROM fedora:latest
# maybe i should use a python-X-mongo specific image ?

RUN dnf install -y libpq libpq-devel

RUN dnf install -y python3 python3-pip python3-devel gcc openssl-devel npm

WORKDIR /flask_app

# python venv
COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# copy needed stuff
COPY .  .

# RUN npm install ?? or just use vite's output served by flask ?

# ports
EXPOSE 5000 
# EXPOSE 5173 ?
