use crate::domain::models::{
    article::ArticleId,
    comment::{Comment, CommentId},
    user_id::UserId
};

pub trait CommentReader {
    type Error;
    
    async fn get_comment(&self, id: &CommentId) -> Result<Option<Comment>, Self::Error>;
    async fn get_comments(
        &self,
        article_id: &ArticleId,
        offset: u32,
        limit: u32
    ) -> Result<Vec<Comment>, Self::Error>;
}

pub trait CommentWriter {
    type Error;
    
    async fn save_comment(&self, comment: &Comment) -> Result<(), Self::Error>;
}

pub trait CommentRemover {
    type Error;
    
    async fn remove_article_comments(
        &self,
        article_id: &ArticleId,
    ) -> Result<(), Self::Error>;
}

pub trait CommentRater {
    type Error;
    async fn rate_comment(&self, comment_id: &CommentId, user_id: &UserId) -> Result<bool, Self::Error>;
    async fn unrate_comment(&self, comment_id: &CommentId, user_id: &UserId) -> Result<bool, Self::Error>;
    async fn is_user_rate_comment(comment_id: &CommentId, user_id: &UserId) -> Result<bool, Self::Error>;
    async fn is_user_rate_comments(
        &self,
        comment_ids: &[CommentId],
        user_id: &UserId,
    ) -> Result<Vec<bool>, Self::Error>;
}

pub trait CommentGateway: 
    CommentReader + 
    CommentWriter + 
    CommentRemover + 
    CommentRater {}