FROM python:3.6

WORKDIR /std_app

ADD . /std_app

COPY requirements.txt /std_app

RUN python3 -m pip install -r requirements.txt

RUN python3 -m pip install ibm_db

EXPOSE 5000

CMD ["python","app.py"]
