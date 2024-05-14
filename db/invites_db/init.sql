CREATE TYPE INVITE_STATUS AS ENUM ('YES', 'NO', 'MAYBE', 'PENDING');
CREATE TABLE "invites" (
    "eventId" INTEGER NOT NULL,
    "username" TEXT NOT NULL,
    "status" INVITE_STATUS NOT NULL DEFAULT 'PENDING',
    PRIMARY KEY ("eventId", "username") -- FOREIGN KEY ("eventId") REFERENCES "events" ("id") ON DELETE CASCADE,
    -- FOREIGN KEY ("username") REFERENCES "users" ("username") ON DELETE CASCADE
);
