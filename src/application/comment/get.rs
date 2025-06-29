use crate::application::common::{
    article_gateway::ArticleReader,
    error::AppError,
    id_provider::IdProvider,
    comment_gateway::CommentGateway,
    interactor::Interactor
};
use crate::domain::{
    models::{
        article::ArticleId,
        comment::CommentId,
        comment_state::CommentState,
        rate_state::RateState,
        user_id::UserId
    },
    services::access::ensure_can_get_comment
};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use utoipa::{IntoParams, ToSchema};

#[derive(Deserialize, IntoParams)]
pub struct GetCommentInput {
    #[param(example = uuid::Uuid::new_v4, value_type = uuid::Uuid)]
    pub id: CommentId
}

#[derive(Serialize, ToSchema)]
pub struct GetCommentOutput {
    #[schema(example = "This is a message content")]
    pub content: String,
    #[schema(example = uuid::Uuid::new_v4, value_type = uuid::Uuid)]
    pub author_id: UserId,
    #[schema(example = uuid::Uuid::new_v4, value_type = uuid::Uuid)]
    pub article_id: ArticleId,
    #[schema(example = uuid::Uuid::new_v4, value_type = uuid::Uuid, nullable = true)]
    pub parent_id: Option<CommentId>,
    #[schema(example = 10)]
    pub rating: i64,
    #[schema(example = "Published")]
    pub state: CommentState,
    
    pub self_rate: RateState,

    pub created_at: DateTime<Utc>,
    pub updated_at: Option<DateTime<Utc>>,
    
}

pub struct GetComment<'interactor> {
    pub id_provider: Box<dyn IdProvider>,
    pub comment_gateway: &'interactor dyn CommentGateway,
    pub article_reader: &'interactor dyn ArticleReader,
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
