use crate::domain::models::{
    article::ArticleId,
    comment::{Comment, CommentId},
    user_id::UserId
};


pub enum CommentGatewayError {
    Critical(String)
}

pub trait CommentReader {

    async fn get_comment(&self, id: &CommentId) -> Result<Option<Comment>, CommentGatewayError>;
    async fn get_comments(
        &self,
        article_id: &ArticleId,
        offset: u32,
        limit: u32
    ) -> Result<Vec<Comment>, CommentGatewayError>;
}

pub trait CommentWriter {

    async fn save_comment(&self, comment: &Comment) -> Result<(), CommentGatewayError>;
}

pub trait CommentRemover {

    async fn remove_article_comments(
        &self,
        article_id: &ArticleId,
    ) -> Result<(), CommentGatewayError>;
}

pub trait CommentRater {
async fn rate_comment(&self, comment_id: &CommentId, user_id: &UserId) -> Result<bool, CommentGatewayError>;
    async fn unrate_comment(&self, comment_id: &CommentId, user_id: &UserId) -> Result<bool, CommentGatewayError>;
    async fn is_user_rate_comment(comment_id: &CommentId, user_id: &UserId) -> Result<bool, CommentGatewayError>;
    async fn is_user_rate_comments(
        &self,
        comment_ids: &[CommentId],
        user_id: &UserId,
    ) -> Result<Vec<bool>, CommentGatewayError>;
}

pub trait CommentGateway: 
    CommentReader + 
    CommentWriter + 
    CommentRemover + 
    CommentRater {}