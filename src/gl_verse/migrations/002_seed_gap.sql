-- GAP basic record.
-- Sources checked on 2026-08-05:
-- https://www.youtube.com/@IDOLFACTORY/playlists
-- https://en.wikipedia.org/wiki/Gap_(TV_series)

INSERT INTO series (
    id,
    title,
    country,
    release_year,
    original_title,
    status,
    synopsis
)
VALUES (
    'gap-2022',
    'GAP: The Series',
    'Tailandia',
    2022,
    'ทฤษฎีสีชมพู',
    'completed',
    'Mon empieza a trabajar para Sam, a quien admira desde joven, y descubre una historia más compleja tras su aparente distancia.'
)
ON CONFLICT(id) DO NOTHING;
