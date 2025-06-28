use std::collections::HashMap;
use crate::application::common::{
    error::AppError,
    id_provider::IdProvider,
    interactor::Interactor,
    tag_gateway::TagReader
};
use crate::domain::{
    services::access::ensure_can_find_tags
};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use utoipa::{IntoParams, ToSchema};
use crate::domain::error::{DomainError, ValidationError};
use crate::domain::services::validator::{validate_page, validate_per_page};

#[derive(Deserialize, ToSchema)]
pub enum  FindArticleTagsOrderBy {
    ArticleCountDesc,
    ArticleCountAsc,
    CreatedAtDesc,
    CreatedAtAsc,
}

#[derive(Deserialize, IntoParams)]
pub struct FindArticleTagsInput {
    #[param(example = 1, default = 1)]
    pub page: u32,
    #[param(example = 10, default = 10)]
    pub per_page: u8,
    #[param(example = "rust", value_type = Option<String>)]
    pub query: Option<String>, // todo validate query length
    #[param(example = "ArticleCountDesc", value_type = String)]
    pub order_by: FindArticleTagsOrderBy
}

#[derive(Serialize, ToSchema)]
pub struct TagItem {
    #[schema(example = "rust")]
    pub title: String,
    /// The number of articles associated with this tag
    #[schema(example = 42)]
    pub article_count: u32,
    pub created_at: DateTime<Utc>
}

#[derive(Serialize, ToSchema)]
pub struct FindArticleTagsOutput(pub Vec<TagItem>);

pub struct FindArticleTags<'interactor> {
    pub id_provider: Box<dyn IdProvider>,
    pub tag_reader: &'interactor dyn TagReader
}

impl Interactor<FindArticleTagsInput, FindArticleTagsOutput> for FindArticleTags<'_> {
    async fn execute(&self, input: FindArticleTagsInput) -> Result<FindArticleTagsOutput, AppError> {
        ensure_can_find_tags(
            self.id_provider.permissions(),
            self.id_provider.user_state(),
        )?;

        let mut validation_err_map = HashMap::<String, ValidationError>::new();
        if let Err(DomainError::Validation((key, err))) = validate_page(input.page) {
            validation_err_map.insert(key, err);
        }
        if let Err(DomainError::Validation((key, err))) = validate_per_page(input.per_page) {
            validation_err_map.insert(key, err);
        }

        if !validation_err_map.is_empty() {
            return Err(AppError::Validation(validation_err_map));
        }

        let tags = self.tag_reader.find_tags(
            input.per_page,
            (input.page - 1).wrapping_mul(input.per_page as u32),
            &input.order_by,
            input.query
        ).await?;
        
        Ok(FindArticleTagsOutput(tags.into_iter().map(|(tag, article_count)| {
            TagItem {
                title: tag.title,
                article_count,
                created_at: tag.created_at
            }
        }).collect::<Vec<_>>()))
    }
}
