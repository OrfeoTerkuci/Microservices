CREATE TABLE "events" (
    "id" SERIAL PRIMARY KEY,
    "title" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "date" DATE NOT NULL,
    "organizerId" INTEGER NOT NULL,
    "isPublic" BOOLEAN NOT NULL DEFAULT TRUE
    -- FOREIGN KEY ("organizerId") REFERENCES "users" ("id") ON DELETE CASCADE
);