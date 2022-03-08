FROM --platform=linux/amd64 python:3.9.7

COPY . /

RUN python -m pip install --upgrade pip
RUN pip install python-dotenv discord python-gitlab

CMD [ "python", "./nomic.py" ]