FROM python:3.9.7

COPY . /

RUN python -m pip install --upgrade pip
RUN pip install python-dotenv discord

CMD [ "python", "./nomic.py" ]