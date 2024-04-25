CREATE TABLE "shared_calendars" (
    "sharing_user_id" INTEGER NOT NULL,
    "receiving_user_id" INTEGER NOT NULL,
    -- FOREIGN KEY ("sharing_user_id") REFERENCES "users" ("id") ON DELETE CASCADE,
    -- FOREIGN KEY ("receiving_user_id") REFERENCES "users" ("id") ON DELETE CASCADE,
    PRIMARY KEY ("sharing_user_id", "receiving_user_id")
);