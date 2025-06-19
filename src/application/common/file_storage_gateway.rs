use crate::application::common::presigned_url::PreSignedUrl;
use crate::domain::models::{
    article::ArticleId,
    file::FileId
};

pub trait FileStorageReader {
    type Error;
    async fn is_exist_file(&self, article_id: &ArticleId, id: &FileId) -> Result<bool, Self::Error>;
}

pub trait FileStorageLinker {
    type Error;
    async fn upload_link(
        &self,
        article_id: &ArticleId,
        file_id: &FileId,
        content_type: &str,
        content_length: (u64, u64),
        expires_in: u64,
    ) -> Result<PreSignedUrl, Self::Error>;
    
    async fn download_link(
        &self,
        article_id: &ArticleId,
        file_id: &FileId
    ) -> Result<String, Self::Error>;
}

pub trait FileStorageRemover {
    type Error;
    async fn remove_file(&self, article_id: &ArticleId, file_id: &FileId) -> Result<(), Self::Error>;
}

pub trait FileStorageGateway: FileStorageReader + FileStorageLinker + FileStorageRemover {}