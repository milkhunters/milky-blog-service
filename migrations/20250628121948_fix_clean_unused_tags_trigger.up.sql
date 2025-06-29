-- 28.06.2025 fix clean_unused_tags trigger

DROP TRIGGER IF EXISTS after_delete_article_tags ON articles_tags;
DROP FUNCTION IF EXISTS clean_unused_tags;

CREATE OR REPLACE FUNCTION clean_unused_tags()
    RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM tags
    WHERE NOT EXISTS (
        SELECT 1 FROM articles_tags
        WHERE tag_id = tags.id
    );
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_article_tags_change
    AFTER INSERT OR UPDATE OR DELETE ON articles_tags
    FOR EACH STATEMENT
EXECUTE FUNCTION clean_unused_tags();