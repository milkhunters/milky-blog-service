use crate::application::common::{
    error::AppError,
    id_provider::IdProvider,
    interactor::Interactor,
    tag_gateway::TagReader
};
use crate::domain::{
    models::tag::TagId,
    services::access::ensure_can_find_tags
};
use chrono::{DateTime, Utc};

pub enum OrderBy {
    ArticleCountDesc,
    ArticleCountAsc,
    CreatedAtDesc,
    CreatedAtAsc,
}

pub struct FindTagInput {
    pub page: u32,
    pub per_page: u8,
    pub query: Option<String>,
    pub order_by: OrderBy
}

pub struct TagItem {
    pub id: TagId,
    pub title: String,
    pub article_count: u32,
    pub created_at: DateTime<Utc>
}

pub type FindTagOutput = Vec<TagItem>;

pub struct FindTag<'interactor> {
    id_provider: &'interactor dyn IdProvider,
    tag_reader: &'interactor dyn TagReader
}

impl Interactor<FindTagInput, FindTagOutput> for FindTag<'_> {
    async fn execute(&self, input: FindTagInput) -> Result<FindTagOutput, AppError> {
        ensure_can_find_tags(
            self.id_provider.permissions(),
            self.id_provider.user_state(),
        )?;

        let tags = self.tag_reader.find_tags(
            input.per_page,
            (input.page - 1).wrapping_mul(input.per_page as u32),
            &input.order_by,
            input.query
        ).await?;
        
        Ok(tags.into_iter().map(|(tag, article_count)| {
            TagItem {
                id: tag.id,
                title: tag.title,
                article_count,
                created_at: tag.created_at
            }
        }).collect::<FindTagOutput>())
    }
}
