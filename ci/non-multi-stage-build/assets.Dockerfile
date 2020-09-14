
# WARNING: keep this file in sync with ./Dockerfile

FROM node:12
WORKDIR /build
COPY package.json .
COPY package-lock.json .
RUN npm i
COPY arcv2_platform/static/src arcv2_platform/static/src
RUN npm run build
