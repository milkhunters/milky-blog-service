-- 20.06.2025 initial migration to create first tables

-- Articles ----------------------------------------------------------------
CREATE TYPE article_state AS ENUM ('Draft', 'Published', 'Archived');

CREATE TABLE IF NOT EXISTS articles (
    id uuid UNIQUE PRIMARY KEY,
    title varchar(255) NOT NULL,
    poster uuid NULL,
    content varchar(32000) NOT NULL,
    state article_state NOT NULL,
    views bigint NOT NULL,
    author_id uuid NOT NULL,

    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NULL
);

-- ArticleTags -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tags (
    id uuid UNIQUE PRIMARY KEY,
    title varchar(64) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE IF NOT EXISTS articles_tags (
    article_id uuid NOT NULL,
    tag_id uuid NOT NULL,

    PRIMARY KEY (article_id, tag_id),
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

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

-- ArticleRate -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS article_rate (
    article_id uuid NOT NULL,
    user_id uuid NOT NULL,

    PRIMARY KEY (article_id, user_id),
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
);

-- ArticleFile -------------------------------------------------------------

CREATE TABLE IF NOT EXISTS article_file (
   id uuid UNIQUE PRIMARY KEY,
   filename varchar(255) NOT NULL,
   content_type varchar(255) NOT NULL,
   article_id uuid NOT NULL,
   is_uploaded boolean NOT NULL,

   created_at TIMESTAMP WITH TIME ZONE NOT NULL,
   updated_at TIMESTAMP WITH TIME ZONE NULL,

   FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
);

-- Comments ----------------------------------------------------------------
CREATE TYPE comment_state AS ENUM ('Deleted', 'Published');

CREATE TABLE IF NOT EXISTS comments (
    id uuid UNIQUE PRIMARY KEY,
    content varchar(1000) NOT NULL,
    author_id uuid NOT NULL,
    article_id uuid NOT NULL,
    parent_id uuid NULL,
    state comment_state NOT NULL,

    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NULL,

    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES comments(id) ON DELETE CASCADE
);

-- CommentRate -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS comment_rate (
    comment_id uuid NOT NULL,
    user_id uuid NOT NULL,

    PRIMARY KEY (comment_id, user_id),
    FOREIGN KEY (comment_id) REFERENCES comments(id) ON DELETE CASCADE
);

-- CommentTree -------------------------------------------------------------
-- """
--     The CommentSubset model
--     («Closure Table» и «Adjacency List»)
-- 
--     # Описание полей
--     ancestor: предок
--     descendant: потомок
--     nearest_ancestor: ближайший предок
--     article: пост
--     level: уровень вложенности
-- 
--     """
-- 
--     __tablename__ = "comment_tree"
-- 
--     id = Column(UUID(), primary_key=True, autoincrement=True)
--     ancestor_id = Column(UUID(as_uuid=True), nullable=False)
--     descendant_id = Column(UUID(as_uuid=True), nullable=False)
--     nearest_ancestor_id = Column(UUID(as_uuid=True), nullable=True)
--     article_id = Column(UUID(as_uuid=True), ForeignKey("articles.id"), nullable=False)
--     article = relationship("models.models.article.Article", back_populates="comments_tree")
--     level = Column(Integer())

CREATE TABLE IF NOT EXISTS comment_tree (
    id uuid UNIQUE PRIMARY KEY,
    parent_id uuid NOT NULL,
    nearest_parent_id uuid NULL,
    child_id uuid NOT NULL,
    
    article_id uuid NOT NULL,
    level integer NOT NULL,

    FOREIGN KEY (parent_id) REFERENCES comments(id) ON DELETE CASCADE,
    FOREIGN KEY (child_id) REFERENCES comments(id) ON DELETE CASCADE,
    FOREIGN KEY (nearest_parent_id) REFERENCES comments(id) ON DELETE CASCADE,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
);