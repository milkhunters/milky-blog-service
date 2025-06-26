use crate::application::common::comment_gateway::CommentGateway;
use crate::application::common::{
    article_gateway::ArticleReader,
    comment_gateway::{
        CommentReader,
        CommentWriter
    },
    error::AppError,
    id_provider::IdProvider,
    interactor::Interactor
};
use crate::domain::error::ValidationError;
use crate::domain::models::comment_state::CommentState;
use crate::domain::{
    error::DomainError,
    models::{
        article::ArticleId,
        comment::{Comment, CommentId}
    },
    services::{
        access::ensure_can_create_comment,
        validator::validate_comment_content
    }
};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Deserialize)]
pub struct CreateCommentInput {
    pub article_id: ArticleId,
    pub content: String,
    pub parent_id: Option<CommentId>,
}

#[derive(Serialize)]
pub struct CreateCommentOutput {
    pub id: CommentId
}

pub struct CreateComment<'interactor> {
    pub id_provider: Box<dyn IdProvider>,
    pub article_reader: &'interactor dyn ArticleReader,
    pub comment_gateway: &'interactor dyn CommentGateway,
}

impl Interactor<CreateCommentInput, CreateCommentOutput> for CreateComment<'_> {
    async fn execute(&self, input: CreateCommentInput) -> Result<CreateCommentOutput, AppError> {
        let article = self.article_reader
            .get_article(&input.article_id)
            .await?
            .ok_or(AppError::NotFound("article_id".into()))?;
        
        ensure_can_create_comment(
            self.id_provider.permissions(),
            self.id_provider.user_state(),
            &article.state
        )?;

        // validate
        let mut validator_err_map = HashMap::<String, ValidationError>::new();
        if let Err(DomainError::Validation((key, val))) = validate_comment_content(&input.content) {
            validator_err_map.insert(key, val);
        }
        
        if let Some(parent_id) = input.parent_id {
            if let Some(parent) = self.comment_gateway.get_comment(&parent_id).await? {
                if parent.article_id != article.id {
                    return Err(AppError::NotFound("parent_id".into()));
                }
                if parent.state == CommentState::Deleted {
                    return Err(AppError::NotFound("parent_id".into()));
                }
            } else {
                return Err(AppError::NotFound("parent_id".into()));
            }
        }

        if !validator_err_map.is_empty() {
            return Err(AppError::Validation(validator_err_map.into()));
        }

        // save
        let comment = Comment::new(
            input.content,
            *self.id_provider.user_id(),
            article.id,
            input.parent_id,
        );

        self.comment_gateway.save(&comment).await?;

        Ok(CreateCommentOutput { id: comment.id })
    }
}
