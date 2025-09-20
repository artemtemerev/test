#Image to pull from
FROM python:3.7-slim

#Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

#Set work directory
WORKDIR /code

#install netcat
RUN apt-get update && apt-get install -y netcat

#Install dependencies
RUN pip install --upgrade pip
COPY Pipfile Pipfile.lock /code/
RUN pip install pipenv && pipenv install --system


#copy entrypoint.sh
COPY ./entrypoint.sh .

#update the permission
#RUN chmod +x /code/entrypoint.sh

#Copy project
COPY . /code/

#run entrypoint.sh
ENTRYPOINT ["/code/entrypoint.sh"]