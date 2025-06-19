use crate::application::common::{
    error::{AppError, ErrorContent},
    article_gateway::ArticleGateway,
    file_map_gateway::FileMapGateway,
    id_provider::IdProvider,
    interactor::Interactor
};
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
use std::collections::HashMap;

pub struct UpdateArticleInput {
    pub id: ArticleId,
    pub title: String,
    pub content: String,
    pub state: ArticleState,
    pub poster: Option<FileId>,
    pub tags: Vec<String>
}

pub struct UpdateArticleOutput {
    pub id: ArticleId
}

pub struct UpdateArticle<'interactor> {
    id_provider: &'interactor dyn IdProvider,
    article_gateway: &'interactor dyn ArticleGateway,
    file_map_gateway: &'interactor dyn FileMapGateway
}

impl Interactor<UpdateArticleInput, UpdateArticleOutput> for UpdateArticle<'_> {
    async fn execute(&self, input: UpdateArticleInput) -> Result<UpdateArticleOutput, AppError> {
        let article_author_id = match self.article_gateway.get_article_author_id(&input.id).await? {
            Some(author_id) => author_id,
            None => return Err(AppError::NotFound(ErrorContent::Message("article not found".into())))
        };
        
        ensure_can_update_article(
            self.id_provider.permissions(),
            self.id_provider.user_state(),
            self.id_provider.user_id(),
            &article_author_id
        )?;

        // validate
        let mut validator_err_map = HashMap::<String, String>::new();
        if let Err(DomainError::Validation(err)) = validate_article_title(&input.title) {
            validator_err_map.insert("title".into(), err);
        }
        if let Err(DomainError::Validation(err)) = validate_article_content(&input.content) {
            validator_err_map.insert("content".into(), err);
        }
        if let Err(DomainError::Validation(err)) = validate_article_tags(&input.tags) {
            validator_err_map.insert("tags".into(), err);
        }
        if !validator_err_map.is_empty() {
            return Err(AppError::Validation(ErrorContent::Map(validator_err_map)));
        }
        
        if let Some(file_id) = input.poster {
            match self.file_map_gateway.get_file(&input.id, &file_id).await? {
                Some(file) => {
                    if !file.is_uploaded {
                        return Err(AppError::Validation(ErrorContent::Message("poster file is not uploaded".into())));
                    }
                    if !self.file_map_gateway.is_file_linked(&input.id, &file_id).await? {
                        return Err(AppError::Validation(ErrorContent::Message("poster file is not linked to this article".into())));
                    }
                },
                None => return Err(AppError::NotFound(ErrorContent::Message("poster file not found".into())))
            }
        }
        
        let mut article = self.article_gateway.get_article(&input.id).await?
            .ok_or_else(|| AppError::NotFound(ErrorContent::Message("article not found".into())))?;
        
        article.update(
            input.title,
            input.poster,
            input.content,
            input.state,
            input.tags.into_iter().map(Tag::new).collect::<Vec<Tag>>()
        );
        
        self.article_gateway.save_article(&article).await?;

        Ok(UpdateArticleOutput { id: article.id })
    }
}
