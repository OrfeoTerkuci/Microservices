FROM node:21.7.1-bookworm

WORKDIR /frontend

COPY frontend .

RUN npm install

EXPOSE 8080