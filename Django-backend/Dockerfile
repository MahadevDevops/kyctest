FROM python:3
ADD . /usr/src/app
WORKDIR /usr/src/app
RUN pip3 install -r requirements.txt
EXPOSE 8000
RUN cd /usr/src/app && ls
CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]
