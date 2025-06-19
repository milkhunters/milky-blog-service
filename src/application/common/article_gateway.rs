use crate::domain::models::article::{Article, ArticleId};
use crate::domain::models::article_state::ArticleState;
use crate::domain::models::tag::TagId;
use crate::domain::models::user_id::UserId;

pub trait ArticleReader {
    type Error;
    async fn get_article(&self, id: &ArticleId) -> Result<Option<Article>, Self::Error>;
    async fn find_articles(
        &self,
        query: Option<String>,
        limit: usize,
        offset: usize,
        order_by: &str,
        state: &ArticleState,
        tags: &[TagId],
        author_id: Option<UserId>,
    ) -> Result<Vec<Article>, Self::Error>;
}

pub trait ArticleWriter {
    type Error;
    async fn save_article(&self, article: &Article) -> Result<(), Self::Error>; 
}

pub trait ArticleRemover {
    type Error;
    async fn remove_article(&self, article_id: &ArticleId) -> Result<(), Self::Error>;
}


pub trait ArticleRater {
    type Error;
    async fn rate_article(&self, article_id: &ArticleId, user_id: &UserId) -> Result<bool, Self::Error>;
    async fn unrate_article(&self, article_id: &ArticleId, user_id: &UserId) -> Result<bool, Self::Error>;
    async fn is_user_rated_article(article_id: &ArticleId, user_id: &UserId) -> Result<bool, Self::Error>;
    async fn is_user_rated_articles(
        &self,
        article_ids: &[ArticleId],
        user_id: &UserId,
    ) -> Result<Vec<bool>, Self::Error>;
}

pub trait ArticleGateway: ArticleReader + ArticleWriter + ArticleRemover + ArticleRater {}
