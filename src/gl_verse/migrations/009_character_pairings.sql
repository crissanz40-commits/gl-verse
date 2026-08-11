ALTER TABLE series_pairings RENAME TO series_pairings_v8;

CREATE TABLE series_pairings (
    id TEXT PRIMARY KEY,
    series_id TEXT NOT NULL,
    acting_pair_id TEXT,
    first_character_id TEXT NOT NULL,
    second_character_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('main', 'supporting')),
    CHECK (first_character_id <> second_character_id),
    FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE CASCADE,
    FOREIGN KEY (acting_pair_id) REFERENCES acting_pairs(id) ON DELETE SET NULL,
    FOREIGN KEY (first_character_id, series_id)
        REFERENCES characters(id, series_id)
        ON DELETE CASCADE,
    FOREIGN KEY (second_character_id, series_id)
        REFERENCES characters(id, series_id)
        ON DELETE CASCADE
);

INSERT INTO series_pairings (
    id, series_id, acting_pair_id, first_character_id, second_character_id, role
)
SELECT id, series_id, acting_pair_id, first_character_id, second_character_id, role
FROM series_pairings_v8;

DROP TABLE series_pairings_v8;

CREATE UNIQUE INDEX uq_series_pairing_characters
    ON series_pairings (
        series_id,
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
WHEN NEW.acting_pair_id IS NOT NULL AND NOT EXISTS (
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
          (first_credit.character_id = NEW.first_character_id
           AND second_credit.character_id = NEW.second_character_id)
          OR
          (first_credit.character_id = NEW.second_character_id
           AND second_credit.character_id = NEW.first_character_id)
      )
)
BEGIN
    SELECT RAISE(ABORT, 'La pareja artística debe corresponder con el reparto de la serie');
END;

CREATE TRIGGER validate_series_pairing_cast_on_update
BEFORE UPDATE OF series_id, acting_pair_id, first_character_id, second_character_id
ON series_pairings
WHEN NEW.acting_pair_id IS NOT NULL AND NOT EXISTS (
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
          (first_credit.character_id = NEW.first_character_id
           AND second_credit.character_id = NEW.second_character_id)
          OR
          (first_credit.character_id = NEW.second_character_id
           AND second_credit.character_id = NEW.first_character_id)
      )
)
BEGIN
    SELECT RAISE(ABORT, 'La pareja artística debe corresponder con el reparto de la serie');
END;
