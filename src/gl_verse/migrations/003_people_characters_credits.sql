CREATE TABLE people (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    stage_name TEXT,
    nationality TEXT
);

CREATE TABLE characters (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    series_id TEXT NOT NULL,
    FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE CASCADE,
    UNIQUE (id, series_id)
);

CREATE TABLE credits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    series_id TEXT NOT NULL,
    person_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (
        role IN ('cast', 'director', 'writer', 'producer')
    ),
    character_id TEXT,
    CHECK (character_id IS NULL OR role = 'cast'),
    FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE CASCADE,
    FOREIGN KEY (person_id) REFERENCES people(id) ON DELETE CASCADE,
    FOREIGN KEY (character_id, series_id)
        REFERENCES characters(id, series_id)
        ON DELETE CASCADE
);

CREATE INDEX idx_characters_series_id ON characters(series_id);
CREATE INDEX idx_credits_series_id ON credits(series_id);
CREATE INDEX idx_credits_person_id ON credits(person_id);
CREATE INDEX idx_credits_character_id ON credits(character_id);

CREATE UNIQUE INDEX uq_credits_with_character
    ON credits(series_id, person_id, role, character_id)
    WHERE character_id IS NOT NULL;

CREATE UNIQUE INDEX uq_credits_without_character
    ON credits(series_id, person_id, role)
    WHERE character_id IS NULL;
