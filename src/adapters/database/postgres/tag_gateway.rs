use crate::application::article::tag::find::FindArticleTagsOrderBy;
use crate::application::common::tag_gateway::{
    TagGateway,
    TagGatewayError,
    TagReader
};
use crate::domain::models::tag::Tag;
use async_trait::async_trait;
use sqlx::Row;

impl From<sqlx::Error> for TagGatewayError {
    fn from(err: sqlx::Error) -> Self {
        TagGatewayError::Critical(err.to_string())
    }
}

impl From<Box<dyn serde::de::StdError + Send + Sync>> for TagGatewayError {
    fn from(err: Box<dyn serde::de::StdError + Send + Sync>) -> Self {
        TagGatewayError::Critical(err.to_string())
    }
}

pub struct PostgresTagGateway {
    pool: sqlx::PgPool
}

impl PostgresTagGateway {
    pub fn new(pool: sqlx::PgPool) -> Self {
        Self { pool }
    }
}

#[async_trait]
impl TagReader for PostgresTagGateway {
    async fn find_tags(
        &self,
        limit: u8,
        offset: u32,
        order_by: &FindArticleTagsOrderBy,
        query: Option<String>
    ) -> Result<Vec<(Tag, u32)>, TagGatewayError> {
        let mut sql = String::from(
            r#"
            SELECT
                t.title, 
                t.created_at,
                COUNT(at.tag_id) AS article_count
            FROM tags t
            LEFT JOIN articles_tags at ON t.id = at.tag_id
            "#
        );

        // Query by title
        let mut where_added = false;
        if query.is_some() {
            sql.push_str(" WHERE t.title ILIKE $1 ");
            where_added = true;
        }
        sql.push_str(" GROUP BY t.id ");

        // Sorting
        sql.push_str(" ORDER BY ");
        match order_by {
            FindArticleTagsOrderBy::ArticleCountDesc => sql.push_str("article_count DESC"),
            FindArticleTagsOrderBy::ArticleCountAsc => sql.push_str("article_count ASC"),
            FindArticleTagsOrderBy::CreatedAtDesc => sql.push_str("t.created_at DESC"),
            FindArticleTagsOrderBy::CreatedAtAsc => sql.push_str("t.created_at ASC"),
        }

        // Pagination
        sql.push_str(" LIMIT $");
        sql.push_str(&format!("{}", if where_added { 2 } else { 1 }));
        sql.push_str(" OFFSET $");
        sql.push_str(&format!("{}", if where_added { 3 } else { 2 }));

        // Build and execute query
        let mut db_query = sqlx::query(&sql);
        if let Some(q) = &query {
            db_query = db_query
                .bind(format!("%{}%", q))
                .bind(limit as i64)
                .bind(offset as i64);
        } else {
            db_query = db_query
                .bind(limit as i64)
                .bind(offset as i64);
        }
        
        let rows = db_query
            .fetch_all(&self.pool)
            .await
            .map_err(|e| TagGatewayError::Critical(e.to_string()))?;

        // Map rows to Tag and count
        let result = rows.into_iter()
            .map(|row| {
                let tag = Tag {
                    title: row.get("title"),
                    created_at: row.get("created_at"),
                };
                let count: i64 = row.get("article_count");
                (tag, count as u32)
            })
            .collect();

        Ok(result)
    }
}

#[async_trait]
impl TagGateway for PostgresTagGateway {}
