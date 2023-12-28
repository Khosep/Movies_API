SELECT
    p.id,
    p.full_name,
    p.updated_at,
    (SELECT json_agg(films_agg)
    	FROM (SELECT pfw.film_work_id,
                    json_agg(pfw.role) roles
              FROM content.person_film_work pfw
              WHERE pfw.person_id = p.id
              GROUP BY 1) films_agg
              ) films
FROM content.person p
LEFT JOIN content.person_film_work pfw ON p.id = pfw.person_id
WHERE p.updated_at > %s
GROUP BY p.id
ORDER BY p.updated_at;