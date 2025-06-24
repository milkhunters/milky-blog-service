use crate::application::common::{
    comment_gateway::{
        CommentReader,
        CommentWriter
    },
    article_gateway::ArticleReader,
    error::AppError,
    id_provider::IdProvider,
    interactor::Interactor
};
use crate::domain::{
    models::comment::CommentId,
    services::access::ensure_can_delete_comment
};
use async_trait::async_trait;

pub struct DeleteCommentInput {
    pub id: CommentId
}

#[async_trait]
pub trait CommentWriterReaderGateway: CommentReader + CommentWriter {}


pub struct DeleteComment<'interactor> {
    id_provider: &'interactor dyn IdProvider,
    comment_gateway: &'interactor dyn CommentWriterReaderGateway,
    article_reader: &'interactor dyn ArticleReader,
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
