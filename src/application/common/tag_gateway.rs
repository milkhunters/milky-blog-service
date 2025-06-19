use async_trait::async_trait;
use crate::domain::models::{
    article::ArticleId,
    tag::{Tag, TagId}
};

pub enum TagGatewayError {
    Critical(String)
}

#[async_trait]
pub trait TagReader {
    async fn get_tags(&self, tag_ids: &[TagId]) -> Result<Vec<Tag>, TagGatewayError>;
    async fn get_tags_by_article(&self, article_id: &ArticleId) -> Result<Vec<Tag>, TagGatewayError>;
}

#[async_trait]
pub trait TagWriter {
    async fn save_tag(&self, tag: &Tag) -> Result<(), TagGatewayError>;
    async fn save_tags(&self, tags: &[Tag]) -> Result<(), TagGatewayError>;
}

#[async_trait]
pub trait TagLinker {
    async fn link_tags(&self, article_id: &ArticleId, tag_ids: &[TagId]) -> Result<(), TagGatewayError>;
}

pub trait TagGateway: TagReader + TagWriter + TagLinker {}