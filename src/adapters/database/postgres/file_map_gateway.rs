use crate::application::common::file_map_gateway::{
    FileMapGateway,
    FileMapGatewayError,
    FileMapReader,
    FileMapRemover,
    FileMapWriter
};
use crate::domain::models::{
    article::ArticleId,
    file::{File, FileId}
};
use async_trait::async_trait;
use sqlx::Row;

impl From<sqlx::Error> for FileMapGatewayError {
    fn from(err: sqlx::Error) -> Self {
        FileMapGatewayError::Critical(err.to_string())
    }
}

impl From<Box<dyn serde::de::StdError + Send + Sync>> for FileMapGatewayError {
    fn from(err: Box<dyn serde::de::StdError + Send + Sync>) -> Self {
        FileMapGatewayError::Critical(err.to_string())
    }
}

pub struct PostgresFileMapGateway {
    pool: sqlx::PgPool
}

impl PostgresFileMapGateway {
    pub fn new(pool: sqlx::PgPool) -> Self {
        Self { pool }
    }
}

#[async_trait]
impl FileMapReader for PostgresFileMapGateway {
    async fn get_file(&self, id: &FileId) -> Result<Option<File>, FileMapGatewayError> {
        let row = sqlx::query("SELECT * FROM article_file WHERE id = $1")
            .bind(id)
            .fetch_optional(&self.pool)
            .await?;
        
        match row {
            Some(row) => Ok(Some(File {
                id: row.try_get("id")?,
                article_id: row.try_get("article_id")?,
                filename: row.try_get("filename")?,
                content_type: row.try_get("content_type")?,
                created_at: row.try_get("created_at")?,
                updated_at: row.try_get("updated_at")?,
                is_uploaded: row.try_get("is_uploaded")?,
            })),
            None => Ok(None)
        }
    }

    async fn get_article_files(&self, article_id: &ArticleId) -> Result<Vec<File>, FileMapGatewayError> {
        let rows = sqlx::query("SELECT * FROM article_file WHERE article_id = $1")
            .bind(article_id)
            .fetch_all(&self.pool)
            .await?;

        Ok(rows.into_iter().map(|row| {
            File {
                id: row.try_get("id").unwrap(),
                article_id: row.try_get("article_id").unwrap(),
                filename: row.try_get("filename").unwrap(),
                content_type: row.try_get("content_type").unwrap(),
                created_at: row.try_get("created_at").unwrap(),
                updated_at: row.try_get("updated_at").unwrap(),
                is_uploaded: row.try_get("is_uploaded").unwrap(),
            }
        }).collect())
    }
}

#[async_trait]
impl FileMapWriter for PostgresFileMapGateway {
    async fn save(&self, file: &File) -> Result<(), FileMapGatewayError> {
        sqlx::query(
            r#"
                INSERT INTO article_file (id, article_id, filename, content_type, created_at, updated_at, is_uploaded) 
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (id) DO UPDATE
                SET article_id = $2,
                    filename = $3,
                    content_type = $4,
                    created_at = $5,
                    updated_at = $6,
                    is_uploaded = $7
            "#
        )
            .bind(&file.id)
            .bind(&file.article_id)
            .bind(&file.filename)
            .bind(&file.content_type)
            .bind(file.created_at)
            .bind(file.updated_at)
            .bind(file.is_uploaded)
            .execute(&self.pool)
            .await?;
        
        Ok(())
    }
}

#[async_trait]
impl FileMapRemover for PostgresFileMapGateway {
    async fn remove(&self, file_id: &FileId) -> Result<(), FileMapGatewayError> {
        sqlx::query("DELETE FROM article_file WHERE id = $1")
            .bind(file_id)
            .execute(&self.pool)
            .await?;
        
        Ok(())
    }
}

#[async_trait]
impl FileMapGateway for PostgresFileMapGateway {}
