-- 25.06.2025 change rate behavior

ALTER TABLE article_rate DROP COLUMN state;
ALTER TABLE comment_rate DROP COLUMN state;

DROP TYPE rate_state;