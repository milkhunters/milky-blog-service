use crate::domain::models::{
    article::ArticleId,
    tag::{Tag, TagId}
};

pub trait TagReader {
    type Error;

    async fn get_tags(&self, tag_ids: &[TagId]) -> Result<Vec<Tag>, Self::Error>;
    async fn get_tags_by_article(&self, article_id: &ArticleId) -> Result<Vec<Tag>, Self::Error>;
}

pub trait TagWriter {
    type Error;

    async fn save_tag(&self, tag: &Tag) -> Result<(), Self::Error>;
    async fn save_tags(&self, tags: &[Tag]) -> Result<(), Self::Error>;
}

pub trait TagLinker {
    type Error;

    async fn link_tags(&self, article_id: &ArticleId, tag_ids: &[TagId]) -> Result<(), Self::Error>;
}

pub trait TagGateway: TagReader + TagWriter + TagLinker {}