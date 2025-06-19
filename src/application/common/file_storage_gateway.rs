use async_trait::async_trait;
use crate::application::common::presigned_url::PreSignedUrl;
use crate::domain::models::{
    article::ArticleId,
    file::FileId
};

pub enum FileStorageError {
    Critical(String)
}

#[async_trait]
pub trait FileStorageReader {
    async fn is_exist_file(&self, article_id: &ArticleId, id: &FileId) -> Result<bool, FileStorageError>;
}

#[async_trait]
pub trait FileStorageLinker {
    async fn upload_link(
        &self,
        article_id: &ArticleId,
        file_id: &FileId,
        content_type: &str,
        content_length: (u64, u64),
        expires_in: u64,
    ) -> Result<PreSignedUrl, FileStorageError>;
    
    async fn download_link(
        &self,
        article_id: &ArticleId,
        file_id: &FileId
    ) -> Result<String, FileStorageError>;
}

#[async_trait]
pub trait FileStorageRemover {
    async fn remove_file(&self, article_id: &ArticleId, file_id: &FileId) -> Result<(), FileStorageError>;
}


pub trait FileStorageGateway: FileStorageReader + FileStorageLinker + FileStorageRemover {}