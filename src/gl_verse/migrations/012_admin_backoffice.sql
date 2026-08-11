CREATE TABLE admin_users (
    username TEXT PRIMARY KEY COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL CHECK (
        created_at GLOB
            '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9]Z'
    )
);

CREATE TABLE admin_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    series_id TEXT NOT NULL,
    changed_at TEXT NOT NULL,
    changes_json TEXT NOT NULL,
    source_id TEXT,
    FOREIGN KEY (username) REFERENCES admin_users(username),
    FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE CASCADE,
    FOREIGN KEY (source_id) REFERENCES catalog_sources(id)
);

CREATE INDEX idx_admin_audit_series
    ON admin_audit_log(series_id, changed_at DESC);
