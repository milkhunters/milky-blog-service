-- 25.06.2025 change rate behavior

CREATE TYPE rate_state AS ENUM ('up', 'neutral', 'down');

ALTER TABLE article_rate
    ADD COLUMN state rate_state NOT NULL DEFAULT 'up';

ALTER TABLE comment_rate
    ADD COLUMN state rate_state NOT NULL DEFAULT 'up';

ALTER TABLE article_rate ALTER COLUMN state DROP DEFAULT;
ALTER TABLE comment_rate ALTER COLUMN state DROP DEFAULT;
