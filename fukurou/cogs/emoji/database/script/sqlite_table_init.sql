BEGIN;

CREATE TABLE IF NOT EXISTS emoji (
    guild_id INTEGER,
    emoji_name TEXT,
    uploader_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    created_at DATETIME,
    PRIMARY KEY (guild_id, emoji_name)
);

CREATE TABLE IF NOT EXISTS emoji_use (
    guild_id INTEGER,
    user_id INTEGER,
    emoji_name TEXT,
    use_count INT,
    PRIMARY KEY (guild_id, user_id, emoji_name),
    FOREIGN KEY (guild_id, emoji_name) REFERENCES emoji(guild_id, emoji_name)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

COMMIT;