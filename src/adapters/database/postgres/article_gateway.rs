use std::collections::HashMap;
use async_trait::async_trait;
use crate::application::{
    article::find::FindArticleOrderBy,
    common::article_gateway::{
        ArticleGateway, 
        ArticleGatewayError, 
        ArticleRater, 
        ArticleReader, 
        ArticleRemover, 
        ArticleWriter
    }
};
use crate::domain::models::{
    article::{Article, ArticleId},
    article_state::ArticleState,
    tag::Tag,
    user_id::UserId,
    rate_state::RateState
};
use sqlx::{
    encode::IsNull,
    error::BoxDynError,
    postgres::PgArguments,
    Database, Decode, Encode, Postgres, Row, Arguments
};


pub struct PostgresArticleGateway {
    pool: sqlx::PgPool
}

impl PostgresArticleGateway {
    pub fn new(pool: sqlx::PgPool) -> Self {
        Self { pool }
    }
}

#[async_trait]
impl ArticleReader for PostgresArticleGateway {
    async fn get_article(&self, id: &ArticleId) -> Result<Option<Article>, ArticleGatewayError> {
        let article_fut = sqlx::query(
            r#"
                SELECT
                id,
                title,
                poster,
                content,
                state,
                views,
                COALESCE((
                    SELECT SUM(
                        CASE state
                            WHEN 'up' THEN 1
                            WHEN 'down' THEN -1
                            ELSE 0
                        END
                    )
                    FROM article_rate 
                    WHERE article_id = articles.id
                ), 0) AS rating,
                author_id,
                created_at,
                updated_at
            FROM articles
            WHERE id = $1
            "#
        )
        .bind(id)
        .fetch_optional(&self.pool);

        let tags_fut = sqlx::query(
            r#"
                SELECT tags.title, tags.created_at FROM tags
                INNER JOIN articles_tags ON tags.id = articles_tags.tag_id
                WHERE articles_tags.article_id = $1
            "#
        )
        .bind(id)
        .fetch_all(&self.pool);

        let (article_row, tags) = tokio::try_join!(
            article_fut,
            tags_fut
        ).map_err(|e| ArticleGatewayError::Critical(e.to_string()))?;

        let article_row = match article_row {
            Some(row) => row,
            None => return Ok(None),
        };

        let tags = tags.into_iter()
            .map(|row| {
                Ok::<_, ArticleGatewayError>(Tag {
                    title: row.try_get("title")?,
                    created_at: row.try_get("created_at")?,
                })
            })
            .collect::<Result<Vec<_>, _>>()?;

        Ok(Some(Article {
            id: article_row.try_get("id")?,
            title: article_row.try_get("title")?,
            poster: article_row.try_get("poster")?,
            content: article_row.try_get("content")?,
            state: article_row.try_get("state")?,
            views: article_row.try_get::<i64, _>("views")? as u32,
            rating: article_row.try_get::<i64, _>("rating")?,
            author_id: article_row.try_get("author_id")?,
            tags,
            created_at: article_row.try_get("created_at")?,
            updated_at: article_row.try_get("updated_at")?
        }))
    }

    async fn find_articles(
        &self,
        query: Option<String>,
        limit: u8,
        offset: u32,
        order_by: &FindArticleOrderBy,
        state: &ArticleState,
        tags: &[String],
        author_id: &Option<UserId>
    ) -> Result<Vec<Article>, ArticleGatewayError> {
        let mut sql = String::from(
            r#"
            SELECT
                id,
                title,
                poster,
                content,
                state,
                views,
                COALESCE((
                    SELECT SUM(
                        CASE state
                            WHEN 'up' THEN 1
                            WHEN 'down' THEN -1
                            ELSE 0
                        END
                    )
                    FROM article_rate 
                    WHERE article_id = articles.id
                ), 0) AS rating,
                author_id,
                created_at,
                updated_at
            FROM articles
            WHERE state = $1
        "#
        );
        
        let mut args = PgArguments::default();
        args.add(state)?;

        let mut param_count = 2;

        // Query find by title, content
        if let Some(q) = &query {
            sql.push_str(&format!(" AND (title ILIKE ${} OR content ILIKE ${}) ", param_count, param_count));
            args.add(format!("%{}%", q))?;
            param_count += 1;
        }

        // Filter records by author_id
        if let Some(author_id) = author_id {
            sql.push_str(&format!(" AND author_id = ${} ", param_count));
            args.add(author_id)?;
            param_count += 1;
        }

        // Filter by tags
        if !tags.is_empty() {
            sql.push_str(&format!(
                " AND id IN (
                SELECT at.article_id
                FROM articles_tags at
                JOIN tags t ON at.tag_id = t.id
                WHERE t.title = ANY(${}::varchar[])
                GROUP BY at.article_id
                HAVING COUNT(DISTINCT t.title) = ${}
            )",
                param_count, param_count + 1
            ));
            args.add(tags)?;
            args.add(tags.len() as i32)?;
            param_count += 2;
        }

        // Sorting
        sql.push_str(" ORDER BY ");
        match order_by {
            FindArticleOrderBy::CreatedAtDesc => sql.push_str("created_at DESC"),
            FindArticleOrderBy::CreatedAtAsc => sql.push_str("created_at ASC"),
            FindArticleOrderBy::ViewsDesc => sql.push_str("views DESC"),
            FindArticleOrderBy::ViewsAsc => sql.push_str("views ASC"),
            FindArticleOrderBy::RatingDesc => sql.push_str("rating DESC"),
            FindArticleOrderBy::RatingAsc => sql.push_str("rating ASC"),
        }

        // Pagination
        sql.push_str(&format!(" LIMIT ${} OFFSET ${}", param_count, param_count + 1));
        args.add(limit as i32)?;
        args.add(offset as i32)?;

        // Execute the query -----------------------------------------------------------------------
        let articles_rows = sqlx::query_with(&sql, args)
            .fetch_all(&self.pool)
            .await
            .map_err(|e| ArticleGatewayError::Critical(e.to_string()))?;

        if articles_rows.is_empty() {
            return Ok(Vec::new());
        }

        // Loading tags ----------------------------------------------------------------------------
        let article_ids: Vec<ArticleId> = articles_rows.iter()
            .map(|row| row.get("id"))
            .collect();
        
        let tags_rows = sqlx::query(
            r#"
            SELECT t.title, t.created_at, at.article_id
            FROM tags t
            INNER JOIN articles_tags at ON t.id = at.tag_id
            WHERE at.article_id = ANY($1)
        "#
        )
            .bind(&article_ids)
            .fetch_all(&self.pool)
            .await
            .map_err(|e| ArticleGatewayError::Critical(e.to_string()))?;
        
        
        let mut tags_map: HashMap<ArticleId, Vec<Tag>> = HashMap::new();
        for row in tags_rows {
            let article_id: ArticleId = row.get("article_id");
            let tag = Tag {
                title: row.get("title"),
                created_at: row.get("created_at"),
            };
            tags_map.entry(article_id).or_default().push(tag);
        }

        // Build result articles -------------------------------------------------------------------
        let articles = articles_rows.into_iter().map(|row| {
            let id: ArticleId = row.try_get("id")?;
            Ok(Article {
                id,
                title: row.try_get("title")?,
                poster: row.try_get("poster")?,
                content: row.try_get("content")?,
                state: row.try_get("state")?,
                views: row.try_get::<i64, _>("views")? as u32,
                rating: row.try_get::<i64, _>("rating")?,
                author_id: row.try_get("author_id")?,
                tags: tags_map.remove(&id).unwrap_or_default(),
                created_at: row.try_get("created_at")?,
                updated_at: row.try_get("updated_at")?,
            })
        }).collect::<Result<Vec<_>, ArticleGatewayError>>()?;

        Ok(articles)
    }

    async fn get_article_author(&self, article_id: &ArticleId) -> Result<Option<UserId>, ArticleGatewayError> {
        let author_fut = sqlx::query(
            r#"
                SELECT author_id
                FROM articles
                WHERE id = $1
            "#
        )
        .bind(article_id)
        .fetch_optional(&self.pool);

        match author_fut.await {
            Ok(Some(row)) => Ok(Some(row.try_get("author_id")?)),
            Ok(None) => Ok(None),
            Err(e) => Err(ArticleGatewayError::Critical(e.to_string())),
        }
    }

    async fn get_article_state(&self, article_id: &ArticleId) -> Result<Option<ArticleState>, ArticleGatewayError> {
        let state_fut = sqlx::query(
            r#"
                SELECT state
                FROM articles
                WHERE id = $1
            "#
        )
        .bind(article_id)
        .fetch_optional(&self.pool);

        match state_fut.await {
            Ok(Some(row)) => Ok(Some(row.try_get("state")?)),
            Ok(None) => Ok(None),
            Err(e) => Err(ArticleGatewayError::Critical(e.to_string())),
        }
    }
}

#[async_trait]
impl ArticleWriter for PostgresArticleGateway {
    async fn save(&self, article: &Article) -> Result<(), ArticleGatewayError> {
        let mut transaction = self.pool.begin().await
            .map_err(|e| ArticleGatewayError::Critical(e.to_string()))?;

        // Insert or update the article
        sqlx::query(
            r#"
                INSERT INTO articles (id, title, poster, content, state, views, author_id, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (id) DO UPDATE
                SET title = $2,
                    poster = $3,
                    content = $4,
                    state = $5,
                    views = $6,
                    author_id = $7,
                    created_at = $8,
                    updated_at = $9
            "#
        )
            .bind(article.id)
            .bind(&article.title)
            .bind(article.poster)
            .bind(&article.content)
            .bind(&article.state)
            .bind(article.views as i64)
            .bind(article.author_id)
            .bind(article.created_at)
            .bind(article.updated_at)
            .execute(&mut *transaction)
            .await
            .map_err(|e| ArticleGatewayError::Critical(
                format!("on article save: {}", e.to_string())
            ))?;

        // Handle tags -----------------------------------------------------------------------------
        // todo optimize this
        sqlx::query(
            r#"DELETE FROM articles_tags WHERE article_id = $1"#
        )
            .bind(article.id)
            .execute(&mut *transaction)
            .await
            .map_err(|e| ArticleGatewayError::Critical(
                format!("on delete articles_tags: {}", e.to_string())
            ))?;

        for tag in &article.tags {
            let tag_id: uuid::Uuid = sqlx::query_scalar(
                r#"
                    WITH new_tag AS (
                        INSERT INTO tags (id, title, created_at)
                        VALUES (gen_random_uuid(), $1, $2)
                        ON CONFLICT (title) DO NOTHING
                        RETURNING id
                    )
                    SELECT id FROM new_tag
                    UNION
                    SELECT id FROM tags WHERE title = $1
                "#
            )
                .bind(&tag.title)
                .bind(tag.created_at)
                .fetch_one(&mut *transaction)
                .await
                .map_err(|e| ArticleGatewayError::Critical(
                    format!("on insert/get new_tag: {}", e.to_string())
                ))?;

            sqlx::query(
                r#"
                    INSERT INTO articles_tags (article_id, tag_id)
                    VALUES ($1, $2)
                "#
            )
                .bind(article.id)
                .bind(tag_id)
                .execute(&mut *transaction)
                .await
                .map_err(|e| ArticleGatewayError::Critical(
                    format!("on insert articles_tags: {}", e.to_string())
                ))?;
        }

        transaction.commit().await.map_err(|e| ArticleGatewayError::Critical(e.to_string()))?;
        Ok(())
    }

    async fn increment_article_views(&self, id: &ArticleId) -> Result<(), ArticleGatewayError> {
        sqlx::query(
            r#"
                UPDATE articles
                SET views = views + 1
                WHERE id = $1
            "#
        )
        .bind(id)
        .execute(&self.pool)
        .await
        .map_err(|e| ArticleGatewayError::Critical(e.to_string()))?;

        Ok(())
    }
}

#[async_trait]
impl ArticleRemover for PostgresArticleGateway {
    async fn remove(&self, article_id: &ArticleId) -> Result<(), ArticleGatewayError> {
        // Tag links will be removed automatically in a cascade fashion
        // Unused tags will also be removed by trigger

        // Remove the article itself
        sqlx::query(
            r#"
                DELETE FROM articles
                WHERE id = $1
            "#
        )
        .bind(article_id)
        .execute(&self.pool)
        .await
        .map_err(|e| ArticleGatewayError::Critical(e.to_string()))?;

        Ok(())
    }
}

#[async_trait]
impl ArticleRater for PostgresArticleGateway {
    async fn rate_article(&self, article_id: &ArticleId, user_id: &UserId, state: &RateState) -> Result<(), ArticleGatewayError> {
        if matches!(state, RateState::Neutral) {
            return sqlx::query(
                r#"
                DELETE FROM article_rate
                WHERE article_id = $1 AND user_id = $2
            "#,
            )
                .bind(article_id)
                .bind(user_id)
                .execute(&self.pool)
                .await
                .map(|_| ())
                .map_err(|e| ArticleGatewayError::Critical(e.to_string()));
        }

        sqlx::query(
            r#"
            INSERT INTO article_rate (article_id, user_id, state)
            VALUES ($1, $2, $3)
            ON CONFLICT (article_id, user_id) DO UPDATE 
                SET state = $3
        "#,
        )
            .bind(article_id)
            .bind(user_id)
            .bind(state)
            .execute(&self.pool)
            .await
            .map(|_| ())
            .map_err(|e| ArticleGatewayError::Critical(e.to_string()))
    }

    async fn user_rate_state(
        &self,
        article_id: &ArticleId,
        user_id: &UserId
    ) -> Result<RateState, ArticleGatewayError> {
        let state: Option<RateState> = sqlx::query_scalar(
            r#"
            SELECT state
            FROM article_rate
            WHERE article_id = $1 AND user_id = $2
        "#
        )
            .bind(article_id)
            .bind(user_id)
            .fetch_optional(&self.pool)
            .await
            .map_err(|e| ArticleGatewayError::Critical(e.to_string()))?;

        Ok(state.unwrap_or(RateState::Neutral))
    }

    async fn user_rate_states(&self, article_ids: &[ArticleId], user_id: &UserId) -> Result<Vec<RateState>, ArticleGatewayError> {
        if article_ids.is_empty() {
            return Ok(Vec::new());
        }

        let rows = sqlx::query(
            r#"
            SELECT
                a.id AS article_id,
                COALESCE(ar.state, 'neutral'::rate_state) AS state
            FROM unnest($1::uuid[]) WITH ORDINALITY AS a(id, idx)
            LEFT JOIN article_rate ar 
                ON a.id = ar.article_id 
                AND ar.user_id = $2
            ORDER BY a.idx
        "#
        )
            .bind(&article_ids)
            .bind(user_id)
            .fetch_all(&self.pool)
            .await
            .map_err(|e| ArticleGatewayError::Critical(e.to_string()))?;

        Ok(rows.into_iter().map(|row| row.get::<RateState, _>("state")).collect())
    }
}

#[async_trait]
impl ArticleGateway for PostgresArticleGateway {}

impl Decode<'_, Postgres> for ArticleState {
    fn decode(value: sqlx::postgres::PgValueRef<'_>) -> Result<Self, sqlx::error::BoxDynError> {
        let state: String = Decode::<'_, Postgres>::decode(value)?;
        match state.as_str() {
            "Draft" => Ok(ArticleState::Draft),
            "Published" => Ok(ArticleState::Published),
            "Archived" => Ok(ArticleState::Archived),
            _ => Err(sqlx::error::BoxDynError::from("unknown article state")),
        }
    }
}

impl Encode<'_, Postgres> for ArticleState {
    fn encode_by_ref(&self, buf: &mut <Postgres as Database>::ArgumentBuffer<'_>) -> Result<IsNull, BoxDynError> {
        let state_str = match self {
            ArticleState::Draft => "Draft",
            ArticleState::Published => "Published",
            ArticleState::Archived => "Archived",
        };
        Encode::<Postgres>::encode_by_ref(&state_str, buf)
    }
}

impl sqlx::Type<Postgres> for ArticleState {
    fn type_info() -> sqlx::postgres::PgTypeInfo {
        sqlx::postgres::PgTypeInfo::with_name("article_state")
    }
}

impl Decode<'_, Postgres> for RateState {
    fn decode(value: sqlx::postgres::PgValueRef<'_>) -> Result<Self, BoxDynError> {
        let state: String = Decode::<'_, Postgres>::decode(value)?;
        match state.as_str() {
            "up" => Ok(RateState::Up),
            "neutral" => Ok(RateState::Neutral),
            "down" => Ok(RateState::Down),
            _ => Err(sqlx::error::BoxDynError::from("unknown rate state")),
        }
    }
}

impl Encode<'_, Postgres> for RateState {
    fn encode_by_ref(&self, buf: &mut <Postgres as Database>::ArgumentBuffer<'_>) -> Result<IsNull, BoxDynError> {
        let state_str = match self {
            RateState::Up => "up",
            RateState::Neutral => "neutral",
            RateState::Down => "down",
        };
        Encode::<Postgres>::encode_by_ref(&state_str, buf)
    }
}

impl sqlx::Type<Postgres> for RateState {
    fn type_info() -> sqlx::postgres::PgTypeInfo {
        sqlx::postgres::PgTypeInfo::with_name("rate_state")
    }
}

impl From<sqlx::Error> for ArticleGatewayError {
    fn from(err: sqlx::Error) -> Self {
        ArticleGatewayError::Critical(err.to_string())
    }
}

impl From<Box<dyn serde::de::StdError + Send + Sync>> for ArticleGatewayError {
    fn from(err: Box<dyn serde::de::StdError + Send + Sync>) -> Self {
        ArticleGatewayError::Critical(err.to_string())
    }
}
