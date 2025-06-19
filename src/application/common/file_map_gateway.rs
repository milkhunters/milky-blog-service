use crate::domain::models::{
    article::ArticleId,
    file::{File, FileId}
};

pub trait FileMapReader {
    type Error;
    async fn get_file(&self, id: &FileId) -> Result<Option<File>, Self::Error>;
}

pub trait FileMapWriter {
    type Error;
    async fn save_file(&self, file: &File) -> Result<(), Self::Error>;
}

pub trait FileMapRemover {
    type Error;
    async fn remove_file(&self, file_id: &FileId) -> Result<(), Self::Error>;
}

pub trait FileArticle {
    type Error;
    async fn get_linked_files(&self, article_id: &ArticleId) -> Result<Vec<File>, Self::Error>;
    async fn is_file_linked(&self, article_id: &ArticleId, file_id: &FileId) -> Result<bool, Self::Error>;
    async fn link_file(&self, article_id: &ArticleId, file: &File) -> Result<(), Self::Error>;
    async fn unlink_file(&self, article_id: &ArticleId) -> Result<(), Self::Error>;
}

pub trait FileGateway: FileMapReader + FileMapWriter + FileMapRemover {}
