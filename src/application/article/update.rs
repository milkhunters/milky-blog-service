use crate::application::common::{
    article_gateway::ArticleGateway,
    error::AppError,
    file_map_gateway::FileMapGateway,
    id_provider::IdProvider,
    interactor::Interactor
};
use crate::domain::error::ValidationError;
use crate::domain::services::access::ensure_can_update_article;
use crate::domain::{
    error::DomainError,
    models::{
        article::ArticleId,
        article_state::ArticleState,
        file::FileId,
        tag::Tag
    },
    services::validator::{
        validate_article_content,
        validate_article_tags,
        validate_article_title
    }
};
use serde::Deserialize;
use std::collections::HashMap;

#[derive(Deserialize)]
pub struct UpdateArticleInput {
    pub id: ArticleId,
    pub title: String,
    pub content: String,
    pub state: ArticleState,
    pub poster: Option<FileId>,
    pub tags: Vec<String>
}

pub struct UpdateArticle<'interactor> {
    pub id_provider: Box<dyn IdProvider>,
    pub article_gateway: &'interactor dyn ArticleGateway,
    pub file_map_gateway: &'interactor dyn FileMapGateway
}

impl Interactor<UpdateArticleInput, ()> for UpdateArticle<'_> {
    async fn execute(&self, input: UpdateArticleInput) -> Result<(), AppError> {
        let article_author_id = match self.article_gateway.get_article_author(&input.id).await? {
            Some(author_id) => author_id,
            None => return Err(AppError::NotFound("id".into()))
        };
        
        ensure_can_update_article(
            self.id_provider.permissions(),
            self.id_provider.user_state(),
            self.id_provider.user_id(),
            &article_author_id
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
        
        if let Some(file_id) = input.poster {
            match self.file_map_gateway.get_file(&file_id).await? {
                Some(file) => {
                    if !file.is_uploaded {
                        return Err(AppError::NotFound("poster".into()));
                    }
                    if !file.article_id.eq(&input.id) {
                        return Err(AppError::NotFound("poster".into()));
                    }
                },
                None => return Err(AppError::NotFound("poster".into()))
            }
        }
        
        let mut article = self.article_gateway.get_article(&input.id).await?
            .ok_or_else(|| AppError::Critical("UpdateArticle article author found, but get_article not found".into()))?;

        article.update(
            input.title,
            input.poster,
            input.content,
            input.state,
            input.tags.into_iter().map(Tag::new).collect::<Vec<Tag>>()
        );
        
        self.article_gateway.save(&article).await?;
        
        Ok(())
    }
}
