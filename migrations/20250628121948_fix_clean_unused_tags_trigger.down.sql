-- 28.06.2025 fix clean_unused_tags trigger

DROP TRIGGER IF EXISTS after_delete_article_tags ON articles_tags;
DROP FUNCTION IF EXISTS clean_unused_tags;

CREATE OR REPLACE FUNCTION clean_unused_tags()
    RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM tags WHERE id IN ( SELECT id FROM OLD )
                       AND NOT EXISTS (
            SELECT 1 FROM articles_tags
            WHERE tag_id = tags.id
        );
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_delete_article_tags
    AFTER DELETE ON articles_tags
    FOR EACH ROW EXECUTE FUNCTION clean_unused_tags();