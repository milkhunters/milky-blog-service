use std::collections::HashMap;
use serde::{Deserialize, Serialize};
use crate::application::common::{
    article_gateway::ArticleWriter,
    error::AppError,
    id_provider::IdProvider,
    interactor::Interactor
};
use crate::domain::{
    error::DomainError,
    models::{
        article::{ArticleId, Article},
        article_state::ArticleState
    },
    services::{
        access::ensure_can_create_article,
        validator::{
            validate_article_title,
            validate_article_content, 
            validate_article_tags
        }
    }
};
use crate::domain::error::ValidationError;
use crate::domain::models::tag::Tag;

#[derive(Deserialize)]
pub struct CreateArticleInput {
    pub title: String,
    pub content: String,
    pub state: ArticleState,
    pub tags: Vec<String>
}

#[derive(Serialize)]
pub struct CreateArticleOutput {
    pub id: ArticleId
}

pub struct CreateArticle<'interactor> {
    id_provider: &'interactor dyn IdProvider,
    article_writer: &'interactor dyn ArticleWriter
}

impl Interactor<CreateArticleInput, CreateArticleOutput> for CreateArticle<'_> {
    async fn execute(&self, input: CreateArticleInput) -> Result<CreateArticleOutput, AppError> {
        ensure_can_create_article(
            self.id_provider.permissions(),
            self.id_provider.user_state(),
        )?;

        // validate
        let mut validator_err_map = HashMap::<String, ValidationError>::new();
        if let Err(DomainError::Validation((key, val))) = validate_article_title(&input.title) {
            validator_err_map.insert(key, val);
        }
        if let Err(DomainError::Validation((key, val))) = validate_article_content(&input.content) {
            validator_err_map.insert(key, val);
        }
        if let Err(DomainError::Validation((key, val))) = validate_article_tags(&input.tags) {
            validator_err_map.insert(key, val);
        }
        if !validator_err_map.is_empty() {
            return Err(AppError::Validation(validator_err_map));
        }
        
        // save
        let article = Article::new(
            input.title,
            None,
            input.content,
            input.tags.into_iter().map(|title| Tag::new(title)).collect(),
            input.state,
            *self.id_provider.user_id(),
        );

        self.article_writer.save(&article).await?;
        
        Ok(CreateArticleOutput { id: article.id })
    }
}
