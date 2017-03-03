FROM python:2.7
ENV PYTHONUNBUFFERED 1
ENV LANG pt_BR.UTF-8
RUN mkdir /code
ADD microerp/ /code/
RUN ls -la /code/
WORKDIR /code
RUN pip install -r requirements.txt
#RUN locale-gen pt_BR.UTF-8
#RUN dpkg-reconfigure locales
