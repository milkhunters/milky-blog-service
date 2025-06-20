use crate::application::common::{
    article_gateway::ArticleReader,
    comment_gateway::{
        CommentWriter,
        CommentReader
    },
    error::AppError,
    id_provider::IdProvider,
    interactor::Interactor
};
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
use std::collections::HashMap;
use async_trait::async_trait;
use crate::domain::models::comment_state::CommentState;

pub struct CreateCommentInput {
    pub article_id: ArticleId,
    pub content: String,
    pub parent_id: Option<CommentId>,
}

pub struct CreateCommentOutput {
    pub id: CommentId
}

#[async_trait]
pub trait CommentWriterReaderGateway: CommentWriter + CommentReader {}


pub struct CreateComment<'interactor> {
    id_provider: &'interactor dyn IdProvider,
    article_reader: &'interactor dyn ArticleReader,
    comment_gateway: &'interactor dyn CommentWriterReaderGateway,
}

impl Interactor<CreateCommentInput, CreateCommentOutput> for CreateComment<'_> {
    async fn execute(&self, input: CreateCommentInput) -> Result<CreateCommentOutput, AppError> {
        let article = self.article_reader
            .get_article(&input.article_id)
            .await?
            .ok_or(AppError::NotFound("article not found".into()))?;
        
        ensure_can_create_comment(
            self.id_provider.permissions(),
            self.id_provider.user_state(),
            &article.state
        )?;

        // validate
        let mut validator_err_map = HashMap::<String, String>::new();
        if let Err(DomainError::Validation(err)) = validate_comment_content(&input.content) {
            validator_err_map.insert("content".into(), err);
        }
        
        if let Some(parent_id) = input.parent_id {
            if let Some(parent) = self.comment_gateway.get_comment(&parent_id).await? {
                if parent.article_id != article.id {
                    validator_err_map.insert("parent_id".into(), "parent comment does not belong to the same article".into());
                }
                if parent.state == CommentState::Deleted {
                    validator_err_map.insert("parent_id".into(), "parent comment is deleted".into());
                }
            } else {
                validator_err_map.insert("parent_id".into(), "parent comment not found".into());
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
