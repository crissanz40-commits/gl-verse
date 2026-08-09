-- Consolidated catalog records checked on 2026-08-09.
--
-- Official / primary sources:
-- "The Loyal Pin" official series playlist — IDOLFACTORY OFFICIAL.
-- Supports: official title, distribution and lead duo.
-- https://www.youtube.com/playlist?list=PLC1B-xGCMfDstfgFLxmnFXIOiZ6ZbkwB5
-- "The Loyal Pin Series" project media kit.
-- Supports: premise, characters and release information.
-- https://theloyalpinseries.com/
-- "Pluto นิทาน ดวงดาว ความรัก Official Trailer" — GMMTV OFFICIAL.
-- Supports: official title, lead cast and characters.
-- https://www.youtube.com/watch?v=cBq6p5lMxvg
-- "23.5 องศาที่โลกเอียง" official playlist — GMMTV.
-- Supports: official title, lead cast and trailer.
-- https://www.gmm-tv.com/contents/playlist/g9ngJ/?v=VB3MJ
-- "The Secret of Us" drama page — Channel 3 Plus.
-- Supports: premise, platform, cast and main characters.
-- https://ch3plus.com/drama/1601?lang=en
-- "AFFAIR รักเล่นกล" production news — CHANGE2561.
-- Supports: official title, production and lead cast.
-- https://www.change2561.com/news/title/558
-- "CIIZE : Rutricha Phapakithi" artist page — GMMTV.
-- Supports: current professional name and portrait.
-- https://www.gmm-tv.com/artists/view/24/
-- CHANGE ARTIST directory — CHANGE2561.
-- Supports: Lookmhee and Sonya professional names and portraits.
-- https://www.change2561.com/changeartist
--
-- Corroborating sources for original titles, dates, cast and characters:
-- https://en.wikipedia.org/wiki/The_Loyal_Pin
-- https://en.wikipedia.org/wiki/Pluto_(Thai_TV_series)
-- https://en.wikipedia.org/wiki/23.5
-- https://en.wikipedia.org/wiki/The_Secret_of_Us_(TV_series)
-- https://en.wikipedia.org/wiki/Affair_(Thai_Drama)

INSERT INTO series (
    id, title, country, release_year, original_title, status, synopsis,
    cover_image_url, cover_image_source_url
)
VALUES
    (
        'the-loyal-pin-2024',
        'The Loyal Pin',
        'Tailandia',
        2024,
        'ปิ่นภักดิ์',
        'completed',
        'Anin y Pin, unidas desde la infancia, intentan proteger su amor frente a las expectativas familiares y de palacio.',
        'https://upload.wikimedia.org/wikipedia/en/4/44/TheLoyalPin.jpg',
        'https://en.wikipedia.org/wiki/The_Loyal_Pin'
    ),
    (
        'pluto-2024',
        'Pluto',
        'Tailandia',
        2024,
        'นิทาน ดวงดาว ความรัก',
        'completed',
        'Ai-oon suplanta a su hermana gemela para cumplir una petición, pero conocer a May transforma el engaño en una relación inesperada.',
        'https://upload.wikimedia.org/wikipedia/en/d/d7/Pluto_2024_Official_Poster.png',
        'https://en.wikipedia.org/wiki/Pluto_(Thai_TV_series)'
    ),
    (
        '23-5-2024',
        '23.5',
        'Tailandia',
        2024,
        '23.5 องศาที่โลกเอียง',
        'completed',
        'Ongsa habla con la popular Sun bajo el nombre de Earth y debe decidir si revela quién está realmente detrás de esa identidad.',
        'https://upload.wikimedia.org/wikipedia/en/9/96/23.5_Official_Poster_%282024%29.jpg',
        'https://en.wikipedia.org/wiki/23.5'
    ),
    (
        'the-secret-of-us-2024',
        'The Secret of Us',
        'Tailandia',
        2024,
        'ใจซ่อนรัก',
        'completed',
        'Fahlada y Earn vuelven a encontrarse después de una ruptura dolorosa y deben enfrentarse a lo que nunca llegaron a explicarse.',
        'https://upload.wikimedia.org/wikipedia/en/9/9a/The_Secret_of_Us_poster_%282024%29.jpeg',
        'https://en.wikipedia.org/wiki/The_Secret_of_Us_(TV_series)'
    ),
    (
        'affair-2024',
        'Affair',
        'Tailandia',
        2024,
        'รักเล่นกล',
        'completed',
        'Wan y Pleng crecen juntas, se separan tras una tragedia familiar y se reencuentran años después con sus sentimientos aún sin resolver.',
        'https://upload.wikimedia.org/wikipedia/en/8/88/Affair_2024_Official_Poster.jpg',
        'https://en.wikipedia.org/wiki/Affair_(Thai_Drama)'
    )
ON CONFLICT(id) DO NOTHING;

INSERT INTO people (
    id, name, stage_name, nationality, image_url, image_source_url
)
VALUES
    (
        'freen-sarocha', 'Sarocha Chankimha', 'Freen', NULL,
        'https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Freen_Sarocha_Chankimha_2026-01-12.jpg/500px-Freen_Sarocha_Chankimha_2026-01-12.jpg',
        'https://commons.wikimedia.org/wiki/File:Freen_Sarocha_Chankimha_2026-01-12.jpg'
    ),
    (
        'becky-armstrong', 'Rebecca Patricia Armstrong', 'Becky', NULL,
        'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Becky_Rebecca_Long_Live_Love_movie_%282023%29.jpg/500px-Becky_Rebecca_Long_Live_Love_movie_%282023%29.jpg',
        'https://commons.wikimedia.org/wiki/File:Becky_Rebecca_Long_Live_Love_movie_(2023).jpg'
    ),
    (
        'namtan-tipnaree', 'Tipnaree Weerawatnodom', 'Namtan', NULL,
        'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Tipnaree_2024-12-27.png/500px-Tipnaree_2024-12-27.png',
        'https://commons.wikimedia.org/wiki/File:Tipnaree_2024-12-27.png'
    ),
    (
        'film-rachanun', 'Rachanun Mahawan', 'Film', NULL,
        'https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Rachanun_Mahawan_at_Seoul_International_Drama_Awards%2C_2_October_2025_04.png/500px-Rachanun_Mahawan_at_Seoul_International_Drama_Awards%2C_2_October_2025_04.png',
        'https://commons.wikimedia.org/wiki/File:Rachanun_Mahawan_at_Seoul_International_Drama_Awards,_2_October_2025_04.png'
    ),
    (
        'milk-pansa', 'Pansa Vosbein', 'Milk', NULL,
        'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/MilkPansaBookfluencer.jpg/500px-MilkPansaBookfluencer.jpg',
        'https://commons.wikimedia.org/wiki/File:MilkPansaBookfluencer.jpg'
    ),
    (
        'love-pattranite', 'Pattranite Limpatiyakorn', 'Love', NULL,
        'https://upload.wikimedia.org/wikipedia/commons/thumb/7/76/Pattranite_2024-11-27.png/500px-Pattranite_2024-11-27.png',
        'https://commons.wikimedia.org/wiki/File:Pattranite_2024-11-27.png'
    ),
    (
        'ciize-rutricha', 'Rutricha Phapakithi', 'Ciize', NULL,
        'https://www.gmm-tv.com/cms/upload_file/vj_floating2026/pic/Ciize_800.jpg',
        'https://www.gmm-tv.com/artists/view/24/'
    ),
    (
        'lingling-sirilak', 'Sirilak Kwong', 'Lingling', NULL,
        'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Lingling_Kwong_%40_The_Secret_Of_Us.png/500px-Lingling_Kwong_%40_The_Secret_Of_Us.png',
        'https://commons.wikimedia.org/wiki/File:Lingling_Kwong_@_The_Secret_Of_Us.png'
    ),
    (
        'orm-kornnaphat', 'Kornnaphat Sethratanapong', 'Orm', NULL,
        'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Orm_Kornnaphat_%40_The_Secret_Of_Us.png/500px-Orm_Kornnaphat_%40_The_Secret_Of_Us.png',
        'https://commons.wikimedia.org/wiki/File:Orm_Kornnaphat_@_The_Secret_Of_Us.png'
    ),
    (
        'lookmhee-punyapat', 'Punyapat Wangpongsathaporn', 'Lookmhee', NULL,
        'https://www.change2561.com/assets/uploads/img/Artist/image/20251223194320_84BD818B-F3F0-4097-9DCC-813BC54D14AE.jpeg',
        'https://www.change2561.com/changeartist'
    ),
    (
        'sonya-saranphat', 'Saranphat Pedersen', 'Sonya', NULL,
        'https://www.change2561.com/assets/uploads/img/Artist/image/20251223184747_B50D049D-5ED1-478C-A46A-9BB754D16AAF.jpeg',
        'https://www.change2561.com/changeartist'
    )
ON CONFLICT(id) DO NOTHING;

INSERT INTO characters (id, name, series_id)
VALUES
    ('sam-gap', 'Sam', 'gap-2022'),
    ('mon-gap', 'Mon', 'gap-2022'),
    ('pin-loyal-pin', 'Pin', 'the-loyal-pin-2024'),
    ('anin-loyal-pin', 'Anin', 'the-loyal-pin-2024'),
    ('ai-oon-pluto', 'Ai-oon', 'pluto-2024'),
    ('may-pluto', 'May', 'pluto-2024'),
    ('ongsa-23-5', 'Ongsa', '23-5-2024'),
    ('sun-23-5', 'Sun', '23-5-2024'),
    ('alpha-23-5', 'Alpha', '23-5-2024'),
    ('fahlada-secret-of-us', 'Fahlada', 'the-secret-of-us-2024'),
    ('earn-secret-of-us', 'Earn', 'the-secret-of-us-2024'),
    ('wan-affair', 'Wan', 'affair-2024'),
    ('pleng-affair', 'Pleng', 'affair-2024')
ON CONFLICT(id) DO NOTHING;

INSERT INTO credits (
    series_id, person_id, role, character_id, cast_importance
)
VALUES
    ('gap-2022', 'freen-sarocha', 'cast', 'sam-gap', 'lead'),
    ('gap-2022', 'becky-armstrong', 'cast', 'mon-gap', 'lead'),
    ('the-loyal-pin-2024', 'freen-sarocha', 'cast', 'pin-loyal-pin', 'lead'),
    ('the-loyal-pin-2024', 'becky-armstrong', 'cast', 'anin-loyal-pin', 'lead'),
    ('pluto-2024', 'namtan-tipnaree', 'cast', 'ai-oon-pluto', 'lead'),
    ('pluto-2024', 'film-rachanun', 'cast', 'may-pluto', 'lead'),
    ('23-5-2024', 'milk-pansa', 'cast', 'ongsa-23-5', 'lead'),
    ('23-5-2024', 'love-pattranite', 'cast', 'sun-23-5', 'lead'),
    ('23-5-2024', 'ciize-rutricha', 'cast', 'alpha-23-5', 'supporting'),
    ('the-secret-of-us-2024', 'lingling-sirilak', 'cast', 'fahlada-secret-of-us', 'lead'),
    ('the-secret-of-us-2024', 'orm-kornnaphat', 'cast', 'earn-secret-of-us', 'lead'),
    ('affair-2024', 'lookmhee-punyapat', 'cast', 'wan-affair', 'lead'),
    ('affair-2024', 'sonya-saranphat', 'cast', 'pleng-affair', 'lead')
ON CONFLICT DO NOTHING;

INSERT INTO acting_pairs (
    id, name, first_person_id, second_person_id, active_since,
    image_url, image_source_url
)
VALUES
    ('freenbecky', 'FreenBecky', 'freen-sarocha', 'becky-armstrong', NULL, NULL, NULL),
    ('namtanfilm', 'NamtanFilm', 'namtan-tipnaree', 'film-rachanun', NULL, NULL, NULL),
    ('milklove', 'MilkLove', 'milk-pansa', 'love-pattranite', NULL, NULL, NULL),
    ('lingorm', 'LingOrm', 'lingling-sirilak', 'orm-kornnaphat', NULL, NULL, NULL),
    ('lmsy', 'LMSY', 'lookmhee-punyapat', 'sonya-saranphat', NULL, NULL, NULL)
ON CONFLICT DO NOTHING;

INSERT INTO series_pairings (
    id, series_id, acting_pair_id, first_character_id, second_character_id, role
)
VALUES
    ('sam-mon-gap', 'gap-2022', 'freenbecky', 'sam-gap', 'mon-gap', 'main'),
    (
        'anin-pin-loyal-pin', 'the-loyal-pin-2024', 'freenbecky',
        'anin-loyal-pin', 'pin-loyal-pin', 'main'
    ),
    (
        'ai-oon-may-pluto', 'pluto-2024', 'namtanfilm',
        'ai-oon-pluto', 'may-pluto', 'main'
    ),
    ('ongsa-sun-23-5', '23-5-2024', 'milklove', 'ongsa-23-5', 'sun-23-5', 'main'),
    (
        'fahlada-earn-secret-of-us', 'the-secret-of-us-2024', 'lingorm',
        'fahlada-secret-of-us', 'earn-secret-of-us', 'main'
    ),
    ('wan-pleng-affair', 'affair-2024', 'lmsy', 'wan-affair', 'pleng-affair', 'main')
ON CONFLICT DO NOTHING;
