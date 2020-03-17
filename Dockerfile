FROM python:3.6.3-slim

ADD poxter/ /poxter/
WORKDIR /poxter/

RUN pip install --upgrade -r requirements.txt

CMD [ "python", "poxter.py" ]
