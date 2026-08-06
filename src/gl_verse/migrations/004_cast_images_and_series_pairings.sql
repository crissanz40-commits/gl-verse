ALTER TABLE series ADD COLUMN cover_image_url TEXT;
ALTER TABLE series ADD COLUMN cover_image_source_url TEXT
    CHECK (
        (cover_image_url IS NULL AND cover_image_source_url IS NULL)
        OR (
            cover_image_url IS NOT NULL
            AND cover_image_source_url IS NOT NULL
            AND (
            cover_image_url LIKE 'http://%'
            OR cover_image_url LIKE 'https://%'
            )
            AND (
                cover_image_source_url LIKE 'http://%'
                OR cover_image_source_url LIKE 'https://%'
            )
        )
    );

ALTER TABLE people ADD COLUMN image_url TEXT;
ALTER TABLE people ADD COLUMN image_source_url TEXT
    CHECK (
        (image_url IS NULL AND image_source_url IS NULL)
        OR (
            image_url IS NOT NULL
            AND image_source_url IS NOT NULL
            AND (
            image_url LIKE 'http://%'
            OR image_url LIKE 'https://%'
            )
            AND (
                image_source_url LIKE 'http://%'
                OR image_source_url LIKE 'https://%'
            )
        )
    );

ALTER TABLE credits ADD COLUMN cast_importance TEXT
    CHECK (
        cast_importance IS NULL
        OR (
            role = 'cast'
            AND cast_importance IN ('lead', 'supporting', 'guest')
        )
    );

CREATE TABLE acting_pairs (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    first_person_id TEXT NOT NULL,
    second_person_id TEXT NOT NULL,
    active_since INTEGER CHECK (active_since IS NULL OR active_since >= 1900),
    image_url TEXT,
    image_source_url TEXT,
    CHECK (first_person_id <> second_person_id),
    CHECK (
        (image_url IS NULL AND image_source_url IS NULL)
        OR (
            image_url IS NOT NULL
            AND image_source_url IS NOT NULL
            AND (
                image_url LIKE 'http://%'
                OR image_url LIKE 'https://%'
            )
            AND (
                image_source_url LIKE 'http://%'
                OR image_source_url LIKE 'https://%'
            )
        )
    ),
    FOREIGN KEY (first_person_id) REFERENCES people(id) ON DELETE CASCADE,
    FOREIGN KEY (second_person_id) REFERENCES people(id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX uq_acting_pair_members
    ON acting_pairs (
        CASE
            WHEN first_person_id < second_person_id THEN first_person_id
            ELSE second_person_id
        END,
        CASE
            WHEN first_person_id < second_person_id THEN second_person_id
            ELSE first_person_id
        END
    );

CREATE INDEX idx_acting_pairs_first_person_id ON acting_pairs(first_person_id);
CREATE INDEX idx_acting_pairs_second_person_id ON acting_pairs(second_person_id);

CREATE TABLE series_pairings (
    id TEXT PRIMARY KEY,
    series_id TEXT NOT NULL,
    acting_pair_id TEXT NOT NULL,
    first_character_id TEXT NOT NULL,
    second_character_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('main', 'supporting')),
    CHECK (first_character_id <> second_character_id),
    FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE CASCADE,
    FOREIGN KEY (acting_pair_id) REFERENCES acting_pairs(id) ON DELETE CASCADE,
    FOREIGN KEY (first_character_id, series_id)
        REFERENCES characters(id, series_id)
        ON DELETE CASCADE,
    FOREIGN KEY (second_character_id, series_id)
        REFERENCES characters(id, series_id)
        ON DELETE CASCADE
);

CREATE UNIQUE INDEX uq_series_pairing_characters
    ON series_pairings (
        series_id,
        acting_pair_id,
        CASE
            WHEN first_character_id < second_character_id THEN first_character_id
            ELSE second_character_id
        END,
        CASE
            WHEN first_character_id < second_character_id THEN second_character_id
            ELSE first_character_id
        END
    );

CREATE INDEX idx_series_pairings_series_id ON series_pairings(series_id);
CREATE INDEX idx_series_pairings_acting_pair_id ON series_pairings(acting_pair_id);

CREATE TRIGGER validate_series_pairing_cast_on_insert
BEFORE INSERT ON series_pairings
WHEN NOT EXISTS (
    SELECT 1
    FROM acting_pairs AS pair
    JOIN credits AS first_credit
        ON first_credit.series_id = NEW.series_id
        AND first_credit.person_id = pair.first_person_id
        AND first_credit.role = 'cast'
    JOIN credits AS second_credit
        ON second_credit.series_id = NEW.series_id
        AND second_credit.person_id = pair.second_person_id
        AND second_credit.role = 'cast'
    WHERE pair.id = NEW.acting_pair_id
      AND (
          (
              first_credit.character_id = NEW.first_character_id
              AND second_credit.character_id = NEW.second_character_id
          )
          OR (
              first_credit.character_id = NEW.second_character_id
              AND second_credit.character_id = NEW.first_character_id
          )
      )
)
BEGIN
    SELECT RAISE(ABORT, 'La pareja debe corresponder con el reparto de la serie');
END;

CREATE TRIGGER validate_series_pairing_cast_on_update
BEFORE UPDATE OF series_id, acting_pair_id, first_character_id, second_character_id
ON series_pairings
WHEN NOT EXISTS (
    SELECT 1
    FROM acting_pairs AS pair
    JOIN credits AS first_credit
        ON first_credit.series_id = NEW.series_id
        AND first_credit.person_id = pair.first_person_id
        AND first_credit.role = 'cast'
    JOIN credits AS second_credit
        ON second_credit.series_id = NEW.series_id
        AND second_credit.person_id = pair.second_person_id
        AND second_credit.role = 'cast'
    WHERE pair.id = NEW.acting_pair_id
      AND (
          (
              first_credit.character_id = NEW.first_character_id
              AND second_credit.character_id = NEW.second_character_id
          )
          OR (
              first_credit.character_id = NEW.second_character_id
              AND second_credit.character_id = NEW.first_character_id
          )
      )
)
BEGIN
    SELECT RAISE(ABORT, 'La pareja debe corresponder con el reparto de la serie');
END;
