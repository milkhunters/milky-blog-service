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
    async fn find_tags(
        &self,
        limit: usize,
        offset: usize,
        order_by_linked: &bool, // true - by linked articles or false - by last add
        query: Option<String>,
    ) -> Result<Vec<Tag>, TagGatewayError>;
}

pub trait TagGateway: TagReader {}