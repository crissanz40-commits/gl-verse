CREATE TABLE platforms (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    website_url TEXT CHECK (
        website_url IS NULL
        OR website_url LIKE 'http://%'
        OR website_url LIKE 'https://%'
    )
);

CREATE UNIQUE INDEX uq_platforms_name ON platforms(name COLLATE NOCASE);

CREATE TABLE availability (
    series_id TEXT NOT NULL,
    platform_id TEXT NOT NULL,
    territory TEXT NOT NULL CHECK (
        territory = 'GLOBAL'
        OR (
            length(territory) = 2
            AND territory = upper(territory)
            AND territory NOT GLOB '*[^A-Z]*'
        )
    ),
    access_model TEXT NOT NULL CHECK (
        access_model IN ('free', 'subscription', 'rental', 'purchase')
    ),
    official_url TEXT NOT NULL CHECK (
        official_url LIKE 'http://%'
        OR official_url LIKE 'https://%'
    ),
    PRIMARY KEY (series_id, platform_id, territory),
    FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE CASCADE,
    FOREIGN KEY (platform_id) REFERENCES platforms(id) ON DELETE CASCADE
);

CREATE INDEX idx_availability_platform_id ON availability(platform_id);
CREATE INDEX idx_availability_territory ON availability(territory);

CREATE TABLE availability_subtitles (
    series_id TEXT NOT NULL,
    platform_id TEXT NOT NULL,
    territory TEXT NOT NULL,
    language TEXT NOT NULL CHECK (length(trim(language)) > 0),
    PRIMARY KEY (series_id, platform_id, territory, language),
    FOREIGN KEY (series_id, platform_id, territory)
        REFERENCES availability(series_id, platform_id, territory)
        ON DELETE CASCADE
);
