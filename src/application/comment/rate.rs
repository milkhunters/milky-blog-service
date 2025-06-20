use crate::application::common::{
    error::{AppError, ErrorContent},
    comment_gateway::{CommentRater, CommentReader},
    article_gateway::ArticleReader,
    id_provider::IdProvider,
    interactor::Interactor
};
use crate::domain::{
    services::access::ensure_can_rate_comment,
    models::comment::CommentId
};
use async_trait::async_trait;

#[async_trait]
pub trait CommentReaderRaterGateway: CommentReader + CommentRater {}

pub struct RateCommentInput {
    pub id: CommentId
}

pub struct RateComment<'interactor> {
    id_provider: &'interactor dyn IdProvider,
    comment_gateway: &'interactor dyn CommentReaderRaterGateway,
    article_reader: &'interactor dyn ArticleReader
}

impl Interactor<RateCommentInput, ()> for RateComment<'_> {
    async fn execute(&self, input: RateCommentInput) -> Result<(), AppError> {
        let comment = match self.comment_gateway.get_comment(&input.id).await? {
            Some(comment) => comment,
            None => return Err(AppError::NotFound(ErrorContent::Message("comment not found".into())))
        };
        
        let article_state = match self.article_reader.get_article_state(&comment.article_id).await? {
            Some(state) => state,
            None => return Err(AppError::NotFound(ErrorContent::Message("article not found".into()))) // critical
        };

        ensure_can_rate_comment(
            self.id_provider.permissions(),
            self.id_provider.user_state(),
            &comment.state,
            &article_state
        )?;

        if self.comment_gateway.is_user_rate_comment(&comment.id, self.id_provider.user_id()).await? {
            self.comment_gateway.unrate_comment(&comment.id, self.id_provider.user_id()).await?;
        } else {
            self.comment_gateway.rate_comment(&comment.id, self.id_provider.user_id()).await?;
        }
        Ok(())
    }
}
