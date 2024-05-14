CREATE TYPE PARTICIPATION_STATUS AS ENUM ('YES', 'NO', 'MAYBE');
CREATE TABLE "rsvp_responses" (
    "eventId" INTEGER NOT NULL,
    "username" TEXT NOT NULL,
    "status" PARTICIPATION_STATUS NOT NULL DEFAULT 'MAYBE',
    PRIMARY KEY ("eventId", "username") -- FOREIGN KEY ("eventId") REFERENCES "events" ("id") ON DELETE CASCADE,
    -- FOREIGN KEY ("username") REFERENCES "users" ("username") ON DELETE CASCADE
);