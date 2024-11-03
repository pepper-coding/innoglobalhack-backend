FROM python:3.12.7 AS image

WORKDIR /app

COPY ./requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

COPY ./src ./dist

CMD ["python", "./dist/main.py"]