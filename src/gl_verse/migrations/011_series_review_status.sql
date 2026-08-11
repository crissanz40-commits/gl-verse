CREATE TABLE series_review_status (
    series_id TEXT PRIMARY KEY,
    status TEXT NOT NULL CHECK (status IN ('pending', 'approved')),
    reviewed_at TEXT,
    CHECK (
        (status = 'pending' AND reviewed_at IS NULL)
        OR
        (
            status = 'approved'
            AND reviewed_at IS NOT NULL
            AND reviewed_at GLOB
                '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9]Z'
        )
    ),
    FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE CASCADE
);
