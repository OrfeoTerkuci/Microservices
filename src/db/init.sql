-- Active: 1713614538968@@127.0.0.1@5432@app
-- CREATE DATABASE "app";
CREATE TYPE INVITE_STATUS AS ENUM ('YES', 'NO', 'MAYBE', 'PENDING');
CREATE TYPE PARTICIPATION_STATUS AS ENUM ('YES', 'NO', 'MAYBE');
CREATE TABLE "users" (
    "id" SERIAL PRIMARY KEY,
    "username" TEXT UNIQUE NOT NULL,
    "password" TEXT NOT NULL
);
CREATE TABLE "events" (
    "id" SERIAL PRIMARY KEY,
    "title" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "date" DATE NOT NULL,
    "organizerId" INTEGER NOT NULL,
    "public" BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY ("organizerId") REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE "invites" (
    "eventId" INTEGER NOT NULL,
    "userId" INTEGER NOT NULL,
    "status" INVITE_STATUS NOT NULL DEFAULT 'PENDING',
    PRIMARY KEY ("eventId", "userId"),
    FOREIGN KEY ("eventId") REFERENCES "events" ("id") ON DELETE CASCADE,
    FOREIGN KEY ("userId") REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE "participations" (
    "eventId" INTEGER NOT NULL,
    "userId" INTEGER NOT NULL,
    "status" PARTICIPATION_STATUS NOT NULL DEFAULT 'MAYBE',
    PRIMARY KEY ("eventId", "userId"),
    FOREIGN KEY ("eventId") REFERENCES "events" ("id") ON DELETE CASCADE,
    FOREIGN KEY ("userId") REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE "shared_calendars" (
    "sharing_user_id" INTEGER NOT NULL,
    "receiving_user_id" INTEGER NOT NULL,
    FOREIGN KEY ("sharing_user_id") REFERENCES "users" ("id") ON DELETE CASCADE,
    FOREIGN KEY ("receiving_user_id") REFERENCES "users" ("id") ON DELETE CASCADE,
    CONSTRAINT "unique_shared_calendar" UNIQUE ("sharing_user_id", "receiving_user_id")
);