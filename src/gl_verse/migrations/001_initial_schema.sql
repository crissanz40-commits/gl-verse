CREATE TABLE IF NOT EXISTS series (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    country TEXT NOT NULL,
    release_year INTEGER NOT NULL CHECK (release_year >= 1900),
    original_title TEXT,
    status TEXT NOT NULL CHECK (
        status IN ('announced', 'airing', 'completed', 'cancelled')
    ),
    synopsis TEXT
);

CREATE INDEX IF NOT EXISTS idx_series_title ON series(title);
CREATE INDEX IF NOT EXISTS idx_series_country ON series(country);
CREATE INDEX IF NOT EXISTS idx_series_release_year ON series(release_year);
