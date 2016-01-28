FROM python:2.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
ADD microerp/ /code/
RUN ls -la /code/
WORKDIR /code
RUN pip install -r requirements.txt
