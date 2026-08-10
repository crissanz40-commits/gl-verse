ALTER TABLE series ADD COLUMN release_date TEXT
    CHECK (
        release_date IS NULL
        OR release_date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
    );

UPDATE series
SET release_date = CASE id
    WHEN 'gap-2022' THEN '2022-11-19'
    WHEN '23-5-2024' THEN '2024-03-08'
    WHEN 'the-secret-of-us-2024' THEN '2024-06-24'
    WHEN 'the-loyal-pin-2024' THEN '2024-08-04'
    WHEN 'affair-2024' THEN '2024-08-30'
    WHEN 'pluto-2024' THEN '2024-10-19'
    WHEN 'whale-store-xoxo-2025' THEN '2025-06-25'
    WHEN 'only-you-2025' THEN '2025-07-18'
    WHEN 'harmony-secret-2025' THEN '2025-07-26'
    WHEN 'enemies-with-benefits-2026' THEN '2026-05-03'
    WHEN 'girl-rules-2026' THEN '2026-03-09'
    ELSE release_date
END
WHERE id IN (
    'gap-2022',
    '23-5-2024',
    'the-secret-of-us-2024',
    'the-loyal-pin-2024',
    'affair-2024',
    'pluto-2024',
    'whale-store-xoxo-2025',
    'only-you-2025',
    'harmony-secret-2025',
    'enemies-with-benefits-2026',
    'girl-rules-2026'
);

CREATE INDEX idx_series_release_date ON series(release_date);
