use async_trait::async_trait;
use crate::domain::models::{
    article::ArticleId,
    comment::{Comment, CommentId},
    user_id::UserId
};
use crate::domain::models::rate_state::RateState;

pub enum CommentGatewayError {
    Critical(String)
}

#[async_trait]
pub trait CommentReader {

    async fn get_comment(&self, id: &CommentId) -> Result<Option<Comment>, CommentGatewayError>;
    async fn get_comments(
        &self,
        article_id: &ArticleId
    ) -> Result<Vec<(Comment, u32)>, CommentGatewayError>;
}

#[async_trait]
pub trait CommentWriter {

    async fn save(&self, comment: &Comment) -> Result<(), CommentGatewayError>;
}

#[async_trait]
pub trait CommentRemover {

    async fn remove_by_article(
        &self,
        article_id: &ArticleId,
    ) -> Result<(), CommentGatewayError>;
}

#[async_trait]
pub trait CommentRater {
    async fn rate_comment(&self, comment_id: &CommentId, user_id: &UserId, state: &RateState) -> Result<(), CommentGatewayError>;
    async fn user_rate_state(&self, comment_id: &CommentId, user_id: &UserId) -> Result<RateState, CommentGatewayError>;
    async fn user_rate_states(
        &self,
        comment_ids: &[CommentId],
        user_id: &UserId,
    ) -> Result<Vec<RateState>, CommentGatewayError>;
}

pub trait CommentGateway: 
    CommentReader + 
    CommentWriter + 
    CommentRemover + 
    CommentRater {}