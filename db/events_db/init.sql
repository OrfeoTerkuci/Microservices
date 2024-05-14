CREATE TABLE "events" (
    "id" SERIAL PRIMARY KEY,
    "title" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "date" DATE NOT NULL,
    "organizer" TEXT NOT NULL,
    "isPublic" BOOLEAN NOT NULL DEFAULT TRUE
    -- FOREIGN KEY ("organizer") REFERENCES "users" ("username") ON DELETE CASCADE
);