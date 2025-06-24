use crate::application::common::{
    article_gateway::ArticleReader,
    comment_gateway::CommentGateway,
    error::AppError,
    id_provider::IdProvider,
    interactor::Interactor
};
use crate::domain::{
    error::DomainError,
    models::comment::CommentId,
    services::{
        access::ensure_can_update_comment,
        validator::validate_comment_content
    }
};
use std::collections::HashMap;
use crate::domain::error::ValidationError;

pub struct UpdateCommentInput {
    pub id: CommentId,
    pub content: String,
}

pub struct UpdateComment<'interactor> {
    id_provider: &'interactor dyn IdProvider,
    article_reader: &'interactor dyn ArticleReader,
    comment_gateway: &'interactor dyn CommentGateway,
}

impl Interactor<UpdateCommentInput, ()> for UpdateComment<'_> {
    async fn execute(&self, input: UpdateCommentInput) -> Result<(), AppError> {
        let mut comment = self.comment_gateway
            .get_comment(&input.id)
            .await?
            .ok_or(AppError::NotFound("id".into()))?;
        
        let article_state = self.article_reader
            .get_article_state(&comment.article_id)
            .await?
            .ok_or(AppError::Critical("UpdateComment comment found but article state not found".into()))?;

        ensure_can_update_comment(
            self.id_provider.permissions(),
            self.id_provider.user_state(),
            self.id_provider.user_id(),
            &comment.author_id,
            &comment.state,
            &article_state
        )?;

        // validate
        let mut validator_err_map = HashMap::<String, ValidationError>::new();
        if let Err(DomainError::Validation((field, err))) = validate_comment_content(&input.content) {
            validator_err_map.insert(field, err);
        }
        if !validator_err_map.is_empty() {
            return Err(AppError::Validation(validator_err_map.into()));
        }

        comment.update(input.content);
        
        self.comment_gateway.save(&comment).await?;

        Ok(())
    }
}
