CREATE TABLE "shared_calendars" (
    "sharingUser" TEXT NOT NULL,
    "receivingUser" TEXT NOT NULL,
    -- FOREIGN KEY ("sharingUser") REFERENCES "users" ("username") ON DELETE CASCADE,
    -- FOREIGN KEY ("receivingUser") REFERENCES "users" ("username") ON DELETE CASCADE,
    PRIMARY KEY ("sharingUser", "receivingUser")
);