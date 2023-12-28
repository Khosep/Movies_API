-- Get all the necessary fields for subsequent transformation and transfer
--   to Elasticsearch (according to the index (see es_index.json))
-- Compared to Postgres fields  (film_work) 'fw.type' and 'fw.created_at' have been removed from output
--   since they are not used in th ES index
SELECT
   fw.id,
   fw.title,
   fw.description,
   fw.rating,
   fw.updated_at,
   COALESCE (
       json_agg(
           DISTINCT jsonb_build_object(
               'person_role', pfw.role,
               'person_id', p.id,
               'person_name', p.full_name
           )
       ) FILTER (WHERE p.id is not null),
       '[]'
   ) as persons,
   array_agg(DISTINCT g.name) as genres
FROM content.film_work fw
LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
LEFT JOIN content.person p ON p.id = pfw.person_id
LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
LEFT JOIN content.genre g ON g.id = gfw.genre_id
WHERE fw.updated_at > %s
GROUP BY fw.id
ORDER BY fw.updated_at;