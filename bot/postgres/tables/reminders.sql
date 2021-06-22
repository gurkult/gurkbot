CREATE TABLE IF NOT EXISTS reminders (
    reminder_id serial NOT NULL,
    message_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    end_time TIMESTAMP NOT NULL,
    content TEXT DEFAULT NULL,
    loop_seconds BIGINT DEFAULT NULL,
    sent BOOLEAN DEFAULT FALSE
);
