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
    FOREIGN KEY (emoji_name) REFERENCES emoji(emoji_name)
);

CREATE TABLE IF NOT EXISTS tag (
    guild_id INTEGER,
    tag_name TEXT,
    PRIMARY KEY (guild_id, tag_name)
);

CREATE TABLE IF NOT EXISTS tagmap (
    guild_id INTEGER PRIMARY KEY,
    emoji_name TEXT,
    tag_name TEXT,
    FOREIGN KEY (emoji_name) REFERENCES emoji(emoji_name),
    FOREIGN KEY (tag_name) REFERENCES tag(tag_name)
);

CREATE TABLE IF NOT EXISTS tag_relation (
    guild_id INTEGER PRIMARY KEY,
    tag_name TEXT,
    parent_name TEXT,
    FOREIGN KEY (tag_name) REFERENCES tag(tag_name),
    FOREIGN KEY (parent_name) REFERENCES tag(tag_name)
);

COMMIT;