use std::collections::HashMap;
use async_trait::async_trait;
use crate::application::{
    article::find::OrderBy,
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
    tag::{Tag, TagId},
    user_id::UserId
};
use sqlx::{
    encode::IsNull,
    error::BoxDynError,
    postgres::PgArguments,
    Database, Decode, Encode, Postgres, Row, Arguments
};

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

pub struct PostgresArticleGateway {
    pool: sqlx::PgPool
}

impl PostgresArticleGateway {
    pub fn new(pool: sqlx::PgPool) -> Self {
        Self { pool }
    }
}

impl Decode<'_, Postgres> for ArticleState {
    fn decode(value: sqlx::postgres::PgValueRef<'_>) -> Result<Self, sqlx::error::BoxDynError> {
        let state: String = Decode::<'_, Postgres>::decode(value)?;
        match state.as_str() {
            "Draft" => Ok(ArticleState::Draft),
            "Published" => Ok(ArticleState::Published),
            "Archived" => Ok(ArticleState::Archived),
            _ => Err(sqlx::error::BoxDynError::from("Unknown article state")),
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
                    state as "state: ArticleState",
                    views,
                    (SELECT COUNT(*) FROM article_rate WHERE article_id = articles.id) AS rating,
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
                SELECT tags.id, tags.title, tags.created_at
                FROM tags
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
                    id: row.try_get("id")?,
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
        order_by: &OrderBy,
        state: &ArticleState,
        tags: &[TagId],
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
            (SELECT COUNT(*) FROM article_rate WHERE article_id = articles.id) AS rating,
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
            args.add(q)?;
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
            SELECT article_id
            FROM articles_tags
            WHERE tag_id = ANY(${}::uuid[])
            GROUP BY article_id
            HAVING COUNT(DISTINCT tag_id) = ${}
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
            OrderBy::CreatedAtDesc => sql.push_str("created_at DESC"),
            OrderBy::CreatedAtAsc => sql.push_str("created_at ASC"),
            OrderBy::ViewsDesc => sql.push_str("views DESC"),
            OrderBy::ViewsAsc => sql.push_str("views ASC"),
            OrderBy::RatingDesc => sql.push_str("rating DESC"),
            OrderBy::RatingAsc => sql.push_str("rating ASC"),
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
            SELECT t.id, t.title, t.created_at, at.article_id
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
                id: row.get("id"),
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
                title: row.get("title"),
                poster: row.get("poster"),
                content: row.get("content"),
                state: row.try_get("state")?,
                views: row.get::<i32, _>("views") as u32,
                rating: row.get::<i64, _>("rating"),
                author_id: row.get("author_id"),
                tags: tags_map.remove(&id).unwrap_or_default(),
                created_at: row.get("created_at"),
                updated_at: row.get("updated_at"),
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
                SELECT state as "state: ArticleState"
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
            .map_err(|e| ArticleGatewayError::Critical(e.to_string()))?;

        // Handle tags
        for tag in &article.tags {
            sqlx::query(
                r#"
                    INSERT INTO tags (id, title, created_at)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (id) DO NOTHING
                "#
            )
                .bind(tag.id)
                .bind(&tag.title)
                .bind(tag.created_at)
                .execute(&mut *transaction)
                .await
                .map_err(|e| ArticleGatewayError::Critical(e.to_string()))?;

            sqlx::query(
                r#"
                    INSERT INTO articles_tags (article_id, tag_id)
                    VALUES ($1, $2)
                    ON CONFLICT DO NOTHING
                "#
            )
                .bind(article.id)
                .bind(tag.id)
                .execute(&mut *transaction)
                .await
                .map_err(|e| ArticleGatewayError::Critical(e.to_string()))?;
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
    async fn rate_article(&self, article_id: &ArticleId, user_id: &UserId) -> Result<bool, ArticleGatewayError> {
        let result = sqlx::query(
            r#"
                INSERT INTO article_rate (article_id, user_id)
                VALUES ($1, $2)
                ON CONFLICT DO NOTHING
            "#
        )
            .bind(article_id)
            .bind(user_id)
            .execute(&self.pool)
            .await;

        match result {
            Ok(res) => Ok(res.rows_affected() > 0),
            Err(e) => Err(ArticleGatewayError::Critical(e.to_string())),
        }
    }

    async fn unrate_article(&self, article_id: &ArticleId, user_id: &UserId) -> Result<bool, ArticleGatewayError> {
        let result = sqlx::query(
            r#"
                DELETE FROM article_rate
                WHERE article_id = $1 AND user_id = $2
            "#
        )
            .bind(article_id)
            .bind(user_id)
            .execute(&self.pool)
            .await;

        match result {
            Ok(res) => Ok(res.rows_affected() > 0),
            Err(e) => Err(ArticleGatewayError::Critical(e.to_string())),
        }
    }

    async fn is_user_rated_article(
        &self,
        article_id: &ArticleId,
        user_id: &UserId
    ) -> Result<bool, ArticleGatewayError> {
        sqlx::query_scalar::<_, bool>(
            r#"
            SELECT EXISTS(
                SELECT 1
                FROM article_rate
                WHERE article_id = $1 AND user_id = $2
            )
        "#
        )
            .bind(article_id)
            .bind(user_id)
            .fetch_one(&self.pool)
            .await
            .map_err(|e| ArticleGatewayError::Critical(e.to_string()))
    }

    async fn is_user_rated_articles(
        &self,
        article_ids: &[ArticleId],
        user_id: &UserId
    ) -> Result<Vec<bool>, ArticleGatewayError> {
        if article_ids.is_empty() {
            return Ok(Vec::new());
        }

        let rows = sqlx::query(
            r#"
        SELECT
            a.id AS article_id,
            EXISTS(
                SELECT 1
                FROM article_rate ar
                WHERE ar.article_id = a.id AND ar.user_id = $2
            ) AS is_rated
        FROM unnest($1::uuid[]) WITH ORDINALITY AS a(id, idx)
        ORDER BY idx
        "#
        )
            .bind(&article_ids)
            .bind(user_id)
            .fetch_all(&self.pool)
            .await
            .map_err(|e| ArticleGatewayError::Critical(e.to_string()))?;

        Ok(rows.into_iter().map(|row| row.get::<bool, _>("is_rated")).collect())
    }
}

#[async_trait]
impl ArticleGateway for PostgresArticleGateway {}
