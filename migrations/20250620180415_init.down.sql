-- 20.06.2025 initial migration to create first tables

DROP TRIGGER IF EXISTS after_delete_article_tags ON articles_tags;

DROP FUNCTION IF EXISTS clean_unused_tags();

DROP TABLE IF EXISTS comment_tree;
DROP TABLE IF EXISTS comment_rate;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS article_file;
DROP TABLE IF EXISTS article_rate;
DROP TABLE IF EXISTS articles_tags;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS articles;

DROP TYPE IF EXISTS comment_state;
DROP TYPE IF EXISTS article_state;
