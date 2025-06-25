use async_trait::async_trait;
use crate::application::common::{
    article_gateway::ArticleReader,
    comment_gateway::{
        CommentReader,
        CommentRater
    },
    error::AppError,
    id_provider::IdProvider,
    interactor::Interactor
};
use crate::domain::{
    models::{
        article::ArticleId,
        comment::CommentId,
        comment_state::CommentState,
        user_id::UserId,
        rate_state::RateState
    },
    services::access::ensure_can_get_comment
};
use chrono::{DateTime, Utc};
use serde::Serialize;

pub struct GetCommentInput {
    pub id: CommentId
}

#[derive(Serialize)]
pub struct GetCommentOutput {
    pub content: String,
    pub author_id: UserId,
    pub article_id: ArticleId,
    pub parent_id: Option<CommentId>,
    pub rating: i64,
    pub state: CommentState,
    
    pub self_rate: RateState,

    pub created_at: DateTime<Utc>,
    pub updated_at: Option<DateTime<Utc>>,
    
}


#[async_trait]
pub trait CommentReaderRaterGateway: CommentReader + CommentRater {}


pub struct GetComment<'interactor> {
    id_provider: &'interactor dyn IdProvider,
    comment_gateway: &'interactor dyn CommentReaderRaterGateway,
    article_reader: &'interactor dyn ArticleReader,
}

impl Interactor<GetCommentInput, GetCommentOutput> for GetComment<'_> {
    async fn execute(&self, input: GetCommentInput) -> Result<GetCommentOutput, AppError> {
        let comment = self.comment_gateway
            .get_comment(&input.id)
            .await?
            .ok_or(AppError::NotFound("id".into()))?;

        let article_state = self.article_reader
            .get_article_state(&comment.article_id)
            .await?
            .ok_or(AppError::Critical("GetComment comment found but article state not found".into()))?;
        

        ensure_can_get_comment(
            self.id_provider.permissions(),
            self.id_provider.user_state(),
            &comment.state,
            &article_state
        )?;
        
        let self_rate = self.comment_gateway.user_rate_state(
            &comment.id,
            self.id_provider.user_id()
        ).await?;

        Ok(GetCommentOutput {
            content: comment.content,
            author_id: comment.author_id,
            article_id: comment.article_id,
            parent_id: comment.parent_id,
            rating: comment.rating,
            state: comment.state,
            self_rate,
            created_at: comment.created_at,
            updated_at: comment.updated_at
        })
    }
}
