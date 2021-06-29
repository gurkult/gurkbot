CREATE TABLE IF NOT EXISTS reminders (
    reminder_id serial NOT NULL PRIMARY KEY,
    jump_url TEXT UNIQUE,
    user_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    end_time TIMESTAMP NOT NULL,
    content VARCHAR(512) DEFAULT NULL
);
