use serde::Deserialize;
use utoipa::IntoParams;
use crate::application::common::{
    article_gateway::ArticleReader,
    error::AppError,
    comment_gateway::CommentGateway,
    id_provider::IdProvider,
    interactor::Interactor
};
use crate::domain::{
    models::comment::CommentId,
    services::access::ensure_can_delete_comment
};

#[derive(Deserialize, IntoParams)]
pub struct DeleteCommentInput {
    #[param(example = uuid::Uuid::new_v4, value_type = uuid::Uuid)]
    pub id: CommentId
}

pub struct DeleteComment<'interactor> {
    pub id_provider: Box<dyn IdProvider>,
    pub comment_gateway: &'interactor dyn CommentGateway,
    pub article_reader: &'interactor dyn ArticleReader,
}

impl Interactor<DeleteCommentInput, ()> for DeleteComment<'_> {
    async fn execute(&self, input: DeleteCommentInput) -> Result<(), AppError> {
        let mut comment = self.comment_gateway
            .get_comment(&input.id)
            .await?
            .ok_or(AppError::NotFound("id".into()))?;
        
        let article_state = self.article_reader
            .get_article_state(&comment.article_id)
            .await?
            .ok_or(AppError::Critical("DeleteComment comment found but article state not found".into()))?;
        
        ensure_can_delete_comment(
            self.id_provider.permissions(),
            self.id_provider.user_state(),
            self.id_provider.user_id(),
            &comment.author_id,
            &comment.state,
            &article_state
        )?;

        comment.mark_deleted();

        self.comment_gateway.save(&comment).await?;

        Ok(())
    }
}
