CREATE TABLE IF NOT EXISTS offtopicnames (
    name VARCHAR(256) UNIQUE PRIMARY KEY,
    num_used SMALLINT check ( num_used >= 0 ) DEFAULT 0
);
