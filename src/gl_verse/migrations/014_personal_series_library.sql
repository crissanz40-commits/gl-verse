CREATE TABLE user_series_entries (
    user_sub TEXT NOT NULL,
    series_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK (
        status IN ('want_to_watch', 'watching', 'watched', 'paused', 'dropped')
    ),
    episodes_watched INTEGER NOT NULL DEFAULT 0 CHECK (
        episodes_watched >= 0 AND episodes_watched <= 9999
    ),
    rating INTEGER CHECK (rating IS NULL OR rating BETWEEN 1 AND 10),
    review_text TEXT CHECK (review_text IS NULL OR length(review_text) <= 2000),
    started_on TEXT CHECK (
        started_on IS NULL OR started_on GLOB
            '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
    ),
    completed_on TEXT CHECK (
        completed_on IS NULL OR completed_on GLOB
            '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
    ),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (user_sub, series_id),
    FOREIGN KEY (user_sub) REFERENCES app_users(google_sub) ON DELETE CASCADE,
    FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE CASCADE
);

CREATE INDEX idx_user_series_entries_user_status
    ON user_series_entries(user_sub, status, updated_at DESC);
