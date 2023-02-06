FROM python:3

WORKDIR /usr/src/Gallery

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY Pipfile Pipfile.lock ./

RUN pip install --upgrade pip
RUN pip install -U pipenv
RUN LIBRARY_PATH=/lib:/usr/lib /bin/sh -c "pipenv install --dev --system"

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY . .

EXPOSE 8000
