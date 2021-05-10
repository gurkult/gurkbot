CREATE TABLE IF NOT EXISTS reminders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT,
    message_id BIGINT UNIQUE,
    end_time TIMESTAMP,
    is_sent BOOLEAN DEFAULT FALSE
);
