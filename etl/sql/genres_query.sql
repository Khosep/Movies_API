SELECT
    g.id,
    g.name,
    g.updated_at
FROM content.genre g
WHERE g.updated_at > %s
ORDER BY g.updated_at;
