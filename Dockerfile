
# WARNING: keep this file in sync with ./ci/non-multi-stage-build/*.Dockerfile

FROM node:12 AS builder
WORKDIR /build
COPY package.json .
COPY package-lock.json .
RUN npm i
COPY arcv2_platform/static/src arcv2_platform/static/src
RUN npm run build


FROM python:3.7
ENV PYTHONUNBUFFERED 1
ENV TZ=Europe/Zurich

RUN git config --global user.email "dev@apptitude.com"
RUN git config --global user.name "Apptitude Automation"

# Install gettext (to collect translations) and timezone data
RUN apt-get update
RUN apt-get install -y gettext tzdata

RUN mkdir /code
WORKDIR /code


# Install python dependencies
ADD requirements.txt /code/
RUN pip install -r requirements.txt

# Copy source code
ADD . /code/
COPY --from=builder /build/arcv2_platform/static/assets /code/arcv2_platform/static/assets

RUN pip install .

RUN flake8 .

# Uncomment the follwing lines to automatically collect static
# files & compile translated messages once the django project
# has been generated.


RUN python manage.py collectstatic --no-input
# RUN python manage.py compilemessages

ENV PATH="/code/bin:${PATH}"

CMD ["./start.sh"]
