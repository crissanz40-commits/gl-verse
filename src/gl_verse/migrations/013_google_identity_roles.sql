DROP TABLE admin_audit_log;
DROP TABLE admin_users;

CREATE TABLE app_users (
    google_sub TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    display_name TEXT,
    picture_url TEXT,
    role TEXT NOT NULL CHECK (role IN ('admin', 'viewer')),
    created_at TEXT NOT NULL,
    last_login_at TEXT NOT NULL
);

CREATE TABLE admin_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    actor_sub TEXT NOT NULL,
    series_id TEXT NOT NULL,
    changed_at TEXT NOT NULL,
    changes_json TEXT NOT NULL,
    source_id TEXT,
    FOREIGN KEY (actor_sub) REFERENCES app_users(google_sub),
    FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE CASCADE,
    FOREIGN KEY (source_id) REFERENCES catalog_sources(id)
);

CREATE INDEX idx_admin_audit_series
    ON admin_audit_log(series_id, changed_at DESC);
