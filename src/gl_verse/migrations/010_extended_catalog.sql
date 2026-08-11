CREATE TABLE companies (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL COLLATE NOCASE UNIQUE,
    country TEXT,
    website_url TEXT CHECK (
        website_url IS NULL OR website_url LIKE 'http://%' OR website_url LIKE 'https://%'
    )
);

CREATE TABLE series_companies (
    series_id TEXT NOT NULL,
    company_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('producer', 'broadcaster', 'distributor')),
    PRIMARY KEY (series_id, company_id, role),
    FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE CASCADE,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

CREATE INDEX idx_series_companies_company ON series_companies(company_id);

CREATE TABLE collections (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL COLLATE NOCASE UNIQUE,
    kind TEXT NOT NULL CHECK (kind IN ('anthology', 'franchise', 'shared_universe')),
    description TEXT
);

CREATE TABLE collection_entries (
    collection_id TEXT NOT NULL,
    series_id TEXT NOT NULL,
    position INTEGER NOT NULL CHECK (position > 0),
    PRIMARY KEY (collection_id, series_id),
    UNIQUE (collection_id, position),
    FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE,
    FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE CASCADE
);

CREATE INDEX idx_collection_entries_series ON collection_entries(series_id);

CREATE TABLE seasons (
    id TEXT PRIMARY KEY,
    series_id TEXT NOT NULL,
    number INTEGER NOT NULL CHECK (number > 0),
    title TEXT,
    release_year INTEGER CHECK (release_year IS NULL OR release_year >= 1900),
    UNIQUE (series_id, number),
    FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE CASCADE
);

CREATE INDEX idx_seasons_series ON seasons(series_id);

CREATE TABLE episodes (
    id TEXT PRIMARY KEY,
    season_id TEXT NOT NULL,
    number INTEGER NOT NULL CHECK (number > 0),
    title TEXT,
    kind TEXT NOT NULL CHECK (kind IN ('regular', 'special')),
    air_date TEXT CHECK (
        air_date IS NULL OR air_date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
    ),
    duration_minutes INTEGER CHECK (duration_minutes IS NULL OR duration_minutes > 0),
    UNIQUE (season_id, number, kind),
    FOREIGN KEY (season_id) REFERENCES seasons(id) ON DELETE CASCADE
);

CREATE INDEX idx_episodes_season ON episodes(season_id);

CREATE TABLE tags (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL COLLATE NOCASE,
    category TEXT NOT NULL CHECK (category IN ('genre', 'trope', 'theme', 'tone')),
    UNIQUE (name, category)
);

CREATE TABLE series_tags (
    series_id TEXT NOT NULL,
    tag_id TEXT NOT NULL,
    PRIMARY KEY (series_id, tag_id),
    FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

CREATE INDEX idx_series_tags_tag ON series_tags(tag_id);

CREATE TABLE content_warnings (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL COLLATE NOCASE UNIQUE,
    description TEXT
);

CREATE TABLE series_content_warnings (
    series_id TEXT NOT NULL,
    warning_id TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high')),
    PRIMARY KEY (series_id, warning_id),
    FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE CASCADE,
    FOREIGN KEY (warning_id) REFERENCES content_warnings(id) ON DELETE CASCADE
);

CREATE INDEX idx_series_content_warnings_warning
    ON series_content_warnings(warning_id);

CREATE TABLE viewing_guides (
    series_id TEXT PRIMARY KEY,
    drama_level TEXT NOT NULL CHECK (
        drama_level IN ('zero_drama', 'light', 'moderate', 'high')
    ),
    ending_type TEXT NOT NULL CHECK (
        ending_type IN (
            'happy_ever_after', 'happy_for_now', 'bittersweet', 'open',
            'sad', 'tragic', 'unknown'
        )
    ),
    ending_note TEXT,
    FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE CASCADE
);

ALTER TABLE provenance_records RENAME TO provenance_records_v9;

CREATE TABLE provenance_records (
    source_id TEXT NOT NULL,
    entity_type TEXT NOT NULL CHECK (
        entity_type IN (
            'series', 'person', 'character', 'acting_pair', 'character_pairing',
            'company', 'series_company', 'platform', 'availability', 'collection',
            'collection_entry', 'season', 'episode', 'tag', 'series_tag',
            'content_warning', 'series_content_warning', 'viewing_guide'
        )
    ),
    entity_id TEXT NOT NULL,
    field_name TEXT NOT NULL,
    checked_on TEXT NOT NULL CHECK (
        checked_on GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
    ),
    status TEXT NOT NULL CHECK (
        status IN ('verified', 'corroborated', 'unverified', 'conflicting')
    ),
    note TEXT,
    PRIMARY KEY (source_id, entity_type, entity_id, field_name),
    FOREIGN KEY (source_id) REFERENCES catalog_sources(id) ON DELETE CASCADE
);

INSERT INTO provenance_records (
    source_id, entity_type, entity_id, field_name, checked_on, status, note
)
SELECT source_id, entity_type, entity_id, field_name, checked_on, status, note
FROM provenance_records_v9;

DROP TABLE provenance_records_v9;

CREATE INDEX idx_provenance_entity
    ON provenance_records(entity_type, entity_id);
