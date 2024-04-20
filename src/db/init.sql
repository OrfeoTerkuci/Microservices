-- Active: 1713614538968@@127.0.0.1@5432@app
-- CREATE DATABASE "app";
CREATE TYPE EVENT_STATUS AS ENUM ('YES', 'NO', 'MAYBE', 'PENDING');
CREATE TABLE "users" (
    "id" SERIAL PRIMARY KEY,
    "username" TEXT NOT NULL,
    "password" TEXT NOT NULL
);
CREATE TABLE "events" (
    "id" SERIAL PRIMARY KEY,
    "title" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "date" DATE NOT NULL,
    "organizer" TEXT NOT NULL,
    "public" BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE TABLE "invitations" (
    "event_id" INTEGER NOT NULL,
    "user_id" INTEGER NOT NULL,
    "status" EVENT_STATUS NOT NULL,
    FOREIGN KEY ("event_id") REFERENCES "events" ("id") ON DELETE CASCADE,
    FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE "calendars" (
    "user_id" INTEGER NOT NULL,
    "event_id" INTEGER NOT NULL,
    FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE CASCADE,
    FOREIGN KEY ("event_id") REFERENCES "events" ("id") ON DELETE CASCADE
);
CREATE TABLE "shared_calendars" (
    "owner_id" INTEGER NOT NULL,
    "user_id" INTEGER NOT NULL,
    FOREIGN KEY ("owner_id") REFERENCES "users" ("id") ON DELETE CASCADE,
    FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE CASCADE
);