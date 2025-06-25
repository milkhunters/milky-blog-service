use crate::application::common::comment_gateway::{
    CommentGateway,
    CommentGatewayError,
    CommentRater,
    CommentReader,
    CommentRemover,
    CommentWriter
};
use crate::domain::models::{
    article::ArticleId,
    comment::{Comment, CommentId},
    comment_state::CommentState,
    user_id::UserId
};
use async_trait::async_trait;
use sqlx::{
    encode::IsNull,
    error::BoxDynError,
    Database, Decode, Encode, Postgres, Row
};
use crate::domain::models::rate_state::RateState;

impl From<sqlx::Error> for CommentGatewayError {
    fn from(err: sqlx::Error) -> Self {
        CommentGatewayError::Critical(err.to_string())
    }
}

impl From<Box<dyn serde::de::StdError + Send + Sync>> for CommentGatewayError {
    fn from(err: Box<dyn serde::de::StdError + Send + Sync>) -> Self {
        CommentGatewayError::Critical(err.to_string())
    }
}

impl Decode<'_, Postgres> for CommentState {
    fn decode(value: sqlx::postgres::PgValueRef<'_>) -> Result<Self, sqlx::error::BoxDynError> {
        let state: String = Decode::<'_, Postgres>::decode(value)?;
        match state.as_str() {
            "Deleted" => Ok(CommentState::Deleted),
            "Published" => Ok(CommentState::Published),
            _ => Err(sqlx::error::BoxDynError::from("Unknown comment state")),
        }
    }
}

impl Encode<'_, Postgres> for CommentState {
    fn encode_by_ref(&self, buf: &mut <Postgres as Database>::ArgumentBuffer<'_>) -> Result<IsNull, BoxDynError> {
        let state_str = match self {
            CommentState::Deleted => "Deleted",
            CommentState::Published => "Published"
        };
        Encode::<Postgres>::encode_by_ref(&state_str, buf)
    }
}

impl sqlx::Type<Postgres> for CommentState {
    fn type_info() -> sqlx::postgres::PgTypeInfo {
        sqlx::postgres::PgTypeInfo::with_name("comment_state")
    }
}

pub struct PostgresCommentGateway {
    pool: sqlx::PgPool
}

impl PostgresCommentGateway {
    pub fn new(pool: sqlx::PgPool) -> Self { Self { pool } }
}


#[async_trait]
impl CommentReader for PostgresCommentGateway {
    async fn get_comment(&self, id: &CommentId) -> Result<Option<Comment>, CommentGatewayError> {
        let comment_row = sqlx::query(
            r#"
                SELECT
                    id,
                    content,
                    state as "state: CommentState",
                    (SELECT COUNT(*) FROM article_rate WHERE article_id = comments.id) AS rating,
                    parent_id,
                    author_id,
                    article_id,
                    created_at,
                    updated_at
                FROM comments
                WHERE id = $1
            "#
        )
            .bind(id)
            .fetch_optional(&self.pool)
            .await?;

        let comment_row = match comment_row {
            Some(row) => row,
            None => return Ok(None)
        };

        Ok(Some(Comment {
            id: comment_row.try_get("id")?,
            content: comment_row.try_get("content")?,
            state: comment_row.try_get("state")?,
            rating: comment_row.try_get::<i64, _>("rating")?,
            author_id: comment_row.try_get("author_id")?,
            article_id: comment_row.try_get("article_id")?,
            parent_id: comment_row.try_get("parent_id")?,
            created_at: comment_row.try_get("created_at")?,
            updated_at: comment_row.try_get("updated_at")?
        }))
    }

    async fn get_comments(&self, article_id: &ArticleId) -> Result<Vec<(Comment, u32)>, CommentGatewayError> {
        let rows = sqlx::query(
            r#"
                SELECT
                    c.id,
                    c.content,
                    c.state as "state: CommentState",
                    (SELECT COUNT(*) FROM comment_rate WHERE comment_id = c.id) AS rating,
                    c.parent_id,
                    c.author_id,
                    c.article_id,
                    c.created_at,
                    c.updated_at,
                    ct.level
                FROM comments c
                JOIN public.comment_tree ct on c.id = ct.child_id
                WHERE ct.article_id = $1 AND ct.parent_id = c.parent_id
                ORDER BY c.created_at
            "#
        )
            .bind(article_id)
            .fetch_all(&self.pool)
            .await?;
        
        Ok(rows.into_iter().map(|row| {
            Ok((
                Comment {
                    id: row.try_get("id")?,
                    content: row.try_get("content")?,
                    state: row.try_get("state")?,
                    rating: row.try_get::<i64, _>("rating")?,
                    author_id: row.try_get("author_id")?,
                    article_id: row.try_get("article_id")?,
                    parent_id: row.try_get("parent_id")?,
                    created_at: row.try_get("created_at")?,
                    updated_at: row.try_get("updated_at")?
                },
                row.try_get::<i32, _>("level")? as u32
            ))
        }).collect::<Result<Vec<_>, sqlx::Error>>()?)
    }
}

#[async_trait]
impl CommentWriter for PostgresCommentGateway {
    async fn save(&self, comment: &Comment) -> Result<(), CommentGatewayError> {
        let mut transaction = self.pool.begin().await?;

        let exists: bool = sqlx::query_scalar(
            "SELECT EXISTS(SELECT 1 FROM comments WHERE id = $1)"
        )
            .bind(&comment.id)
            .fetch_one(&mut *transaction)
            .await?;

        
        if exists {
            sqlx::query(
            r#"
            UPDATE comments 
            SET content = $2,
                state = $3,
                author_id = $4,
                article_id = $5,
                parent_id = $6,
                created_at = $7,
                updated_at = $8
            WHERE id = $1
            "#
        )
                .bind(&comment.content)
                .bind(&comment.state)
                .bind(&comment.author_id)
                .bind(&comment.article_id)
                .bind(&comment.parent_id)
                .bind(&comment.created_at)
                .bind(&comment.updated_at)
                .execute(&mut *transaction)
                .await?;
        } else {
            sqlx::query(
            r#"
            INSERT INTO comments (id, content, state, author_id, article_id, parent_id, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            "#
            )
                .bind(&comment.id)
                .bind(&comment.content)
                .bind(&comment.state)
                .bind(&comment.author_id)
                .bind(&comment.article_id)
                .bind(&comment.parent_id)
                .bind(&comment.created_at)
                .bind(&comment.updated_at)
                .execute(&mut *transaction)
                .await?;

            // Insert into comment_tree
            let parent_level = if let Some(parent_id) = comment.parent_id {
                sqlx::query_scalar(
                r#"SELECT level FROM comment_tree WHERE parent_id = $1 AND child_id = $1"#
                )
                    .bind(parent_id)
                    .fetch_optional(&mut *transaction)
                    .await?
                    .map(|level: i32| level + 1)
                    .unwrap_or(0)
            } else {
                0
            };
            
            sqlx::query(
            r#"
                INSERT INTO comment_tree (parent_id, child_id, nearest_parent_id, article_id, level)
                SELECT parent_id, $1, $2, $3, $4
                FROM comment_tree
                WHERE child_id = $2
                UNION ALL
                SELECT $1, $1, $2, $3, $4
            "#
            )
                .bind(&comment.id)
                .bind(comment.parent_id)
                .bind(&comment.article_id)
                .bind(parent_level)
                .execute(&mut *transaction)
                .await?;
        }

        transaction.commit().await?;
        Ok(())
    }
}

#[async_trait]
impl CommentRemover for PostgresCommentGateway {
    async fn remove_by_article(&self, article_id: &ArticleId) -> Result<(), CommentGatewayError> {
        sqlx::query(r#"DELETE FROM comments WHERE article_id = $1"#)
            .bind(article_id)
            .execute(&self.pool)
            .await?;
        Ok(())
    }
}

#[async_trait]
impl CommentRater for PostgresCommentGateway {
    async fn rate_comment(&self, comment_id: &ArticleId, user_id: &UserId, state: &RateState) -> Result<(), CommentGatewayError> {
        let result = sqlx::query(
            r#"
                INSERT INTO comment_rate (comment_id, user_id, state)
                VALUES ($1, $2, $3)
                ON CONFLICT DO NOTHING
            "#
        )
            .bind(comment_id)
            .bind(user_id)
            .bind(state)
            .execute(&self.pool)
            .await;

        match result {
            Ok(_) => Ok(()),
            Err(e) => Err(CommentGatewayError::Critical(e.to_string())),
        }
    }

    async fn user_rate_state(
        &self,
        comment_id: &CommentId,
        user_id: &UserId
    ) -> Result<RateState, CommentGatewayError> {
        let state: Option<RateState> = sqlx::query_scalar(
            r#"
            SELECT state
            FROM comment_rate
            WHERE comment_id = $1 AND user_id = $2
        "#
        )
            .bind(comment_id)
            .bind(user_id)
            .fetch_optional(&self.pool)
            .await
            .map_err(|e| CommentGatewayError::Critical(e.to_string()))?;

        Ok(state.unwrap_or(RateState::Neutral))
    }

    async fn user_rate_states(&self, comment_ids: &[CommentId], user_id: &UserId) -> Result<Vec<RateState>, CommentGatewayError> {
        if comment_ids.is_empty() {
            return Ok(Vec::new());
        }

        let rows = sqlx::query(
            r#"
            SELECT
                a.id AS comment_id,
                COALESCE(ar.state, 'neutral'::rate_state) AS "state: RateState"
            FROM unnest($1::uuid[]) WITH ORDINALITY AS a(id, idx)
            LEFT JOIN comment_rate ar 
                ON a.id = ar.comment_id 
                AND ar.user_id = $2
            ORDER BY a.idx
        "#
        )
            .bind(&comment_ids)
            .bind(user_id)
            .fetch_all(&self.pool)
            .await
            .map_err(|e| CommentGatewayError::Critical(e.to_string()))?;

        Ok(rows.into_iter().map(|row| row.get::<RateState, _>("state")).collect())
    }
}

#[async_trait]
impl CommentGateway for PostgresCommentGateway {}