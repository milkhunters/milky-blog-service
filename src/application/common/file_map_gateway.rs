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
}

#[async_trait]
pub trait FileMapWriter {
    async fn save_file(&self, file: &File) -> Result<(), FileMapGatewayError>;
}

#[async_trait]
pub trait FileMapRemover {
    async fn remove_file(&self, file_id: &FileId) -> Result<(), FileMapGatewayError>;
}

#[async_trait]
pub trait FileArticle {
    async fn get_linked_files(&self, article_id: &ArticleId) -> Result<Vec<File>, FileMapGatewayError>;
    async fn is_file_linked(&self, article_id: &ArticleId, file_id: &FileId) -> Result<bool, FileMapGatewayError>;
    async fn link_file(&self, article_id: &ArticleId, file: &File) -> Result<(), FileMapGatewayError>;
    async fn unlink_file(&self, article_id: &ArticleId) -> Result<(), FileMapGatewayError>;
}

pub trait FileGateway: FileMapReader + FileMapWriter + FileMapRemover + FileArticle {}
