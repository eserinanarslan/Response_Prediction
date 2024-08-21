FROM python:3.10-slim

ADD requirements.txt /.
RUN pip install -r /requirements.txt

ADD . /code/

WORKDIR /code

CMD ["main.py"]
ENTRYPOINT ["python"]

#ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]