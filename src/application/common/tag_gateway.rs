use crate::domain::models::tag::Tag;
use crate::application::article::tag::find::FindArticleTagsOrderBy;
use async_trait::async_trait;

pub enum TagGatewayError {
    Critical(String)
}

#[async_trait]
pub trait TagReader {
    async fn find_tags(
        &self,
        limit: u8,
        offset: u32,
        order_by: &FindArticleTagsOrderBy,
        query: Option<String>,
    ) -> Result<Vec<(Tag, u32)>, TagGatewayError>;
}

pub trait TagGateway: TagReader + Send + Sync {}