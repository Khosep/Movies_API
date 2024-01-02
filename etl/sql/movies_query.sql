-- Get all the necessary fields for subsequent transformation and transfer
--   to Elasticsearch (according to the index (see movies_es_index.json))
-- Compared to Postgres fields  (film_work) 'fw.type' and 'fw.created_at' have been removed from output
--   since they are not used in th ES index
SELECT
   fw.id,
   fw.title,
   fw.rating,
   fw.description,
   fw.updated_at,
   COALESCE (
       json_agg(
            DISTINCT jsonb_build_object(
           		'id', g.id,
           		'name', g.name
       		)
       ),
       '[]'
       ) as genres,
   COALESCE (
       json_agg(
            DISTINCT jsonb_build_object(
                'id', p.id,
                'full_name', p.full_name
           )
       ) FILTER (WHERE pfw.role = 'actor'),
       '[]'
   ) as actors,
   COALESCE (
       json_agg(
            DISTINCT jsonb_build_object(
                'id', p.id,
                'full_name', p.full_name
           )
       ) FILTER (WHERE pfw.role = 'writer'),
       '[]'
   ) as writers,
   COALESCE (
       json_agg(
            DISTINCT jsonb_build_object(
                'id', p.id,
                'full_name', p.full_name
           )
       ) FILTER (WHERE pfw.role = 'director'),
       '[]'
   ) as directors
FROM content.film_work fw
LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
LEFT JOIN content.person p ON p.id = pfw.person_id
LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
LEFT JOIN content.genre g ON g.id = gfw.genre_id
WHERE fw.updated_at > %s
GROUP BY fw.id
ORDER BY fw.updated_at;