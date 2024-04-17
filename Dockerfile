FROM node:21.7.1-bookworm

WORKDIR /src/frontend

COPY src/frontend .

RUN npm install

EXPOSE 8080