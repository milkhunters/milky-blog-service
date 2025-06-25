use async_trait::async_trait;
use crate::application::article::find::OrderBy;
use crate::domain::models::{
    article::{Article, ArticleId},
    article_state::ArticleState,
    tag::TagId,
    user_id::UserId
};
use crate::domain::models::rate_state::RateState;

pub enum ArticleGatewayError {
    Critical(String)
}

#[async_trait]
pub trait ArticleReader {
    async fn get_article(&self, id: &ArticleId) -> Result<Option<Article>, ArticleGatewayError>;
    async fn find_articles(
        &self,
        query: Option<String>,
        limit: u8,
        offset: u32,
        order_by: &OrderBy,
        state: &ArticleState,
        tags: &[TagId],
        author_id: &Option<UserId>,
    ) -> Result<Vec<Article>, ArticleGatewayError>;
    async fn get_article_author(&self, article_id: &ArticleId) -> Result<Option<UserId>, ArticleGatewayError>;
    async fn get_article_state(
        &self,
        article_id: &ArticleId,
    ) -> Result<Option<ArticleState>, ArticleGatewayError>;
}

#[async_trait]
pub trait ArticleWriter {
    async fn save(&self, article: &Article) -> Result<(), ArticleGatewayError>;
    async fn increment_article_views(&self, id: &ArticleId) -> Result<(), ArticleGatewayError>;
}

#[async_trait]
pub trait ArticleRemover {
    async fn remove(&self, article_id: &ArticleId) -> Result<(), ArticleGatewayError>;
}

#[async_trait]
pub trait ArticleRater {
    async fn rate_article(&self, article_id: &ArticleId, user_id: &UserId, state: &RateState) -> Result<(), ArticleGatewayError>;
    async fn user_rate_state(&self, article_id: &ArticleId, user_id: &UserId) -> Result<RateState, ArticleGatewayError>;
    async fn user_rate_states(
        &self,
        article_ids: &[ArticleId],
        user_id: &UserId,
    ) -> Result<Vec<RateState>, ArticleGatewayError>;
}

#[async_trait]
pub trait ArticleGateway: ArticleReader + ArticleWriter + ArticleRemover + ArticleRater {}
