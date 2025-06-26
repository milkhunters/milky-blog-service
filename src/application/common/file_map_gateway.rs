use async_trait::async_trait;
use crate::domain::models::{
    article::ArticleId,
    file::{File, FileId}
};


pub enum FileMapGatewayError {
    Critical(String)
}

#[async_trait]
pub trait FileMapReader {
    async fn get_file(&self, id: &FileId) -> Result<Option<File>, FileMapGatewayError>;
    async fn get_article_files(&self, article_id: &ArticleId) -> Result<Vec<File>, FileMapGatewayError>;

}

#[async_trait]
pub trait FileMapWriter {
    async fn save(&self, file: &File) -> Result<(), FileMapGatewayError>;
}

#[async_trait]
pub trait FileMapRemover {
    async fn remove(&self, file_id: &FileId) -> Result<(), FileMapGatewayError>;
}

pub trait FileMapGateway: FileMapReader + FileMapWriter + FileMapRemover + Send + Sync {}
