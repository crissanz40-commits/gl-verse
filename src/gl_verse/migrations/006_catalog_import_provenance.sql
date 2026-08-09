CREATE TABLE catalog_sources (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    source_type TEXT NOT NULL CHECK (
        source_type IN ('official', 'platform', 'press', 'interview', 'database', 'community')
    ),
    publisher TEXT,
    published_on TEXT CHECK (
        published_on IS NULL OR published_on GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
    )
);

CREATE UNIQUE INDEX uq_catalog_sources_url ON catalog_sources(url);

CREATE TABLE provenance_records (
    source_id TEXT NOT NULL,
    entity_type TEXT NOT NULL CHECK (
        entity_type IN (
            'series', 'person', 'character', 'acting_pair', 'character_pairing',
            'company', 'platform', 'availability', 'collection', 'season', 'episode',
            'viewing_guide'
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

CREATE INDEX idx_provenance_entity
    ON provenance_records(entity_type, entity_id);
