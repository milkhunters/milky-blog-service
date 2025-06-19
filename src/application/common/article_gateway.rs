use crate::domain::models::{
    article::{Article, ArticleId},
    article_state::ArticleState,
    tag::TagId,
    user_id::UserId
};

pub enum ArticleGatewayError {
    Critical(String)
}

pub trait ArticleReader {
    async fn get_article(&self, id: &ArticleId) -> Result<Option<Article>, ArticleGatewayError>;
    async fn find_articles(
        &self,
        query: Option<String>,
        limit: usize,
        offset: usize,
        order_by: &str,
        state: &ArticleState,
        tags: &[TagId],
        author_id: Option<&UserId>,
    ) -> Result<Vec<Article>, ArticleGatewayError>;
}

pub trait ArticleWriter {
    async fn save_article(&self, article: &Article) -> Result<(), ArticleGatewayError>; 
}

pub trait ArticleRemover {
    async fn remove_article(&self, article_id: &ArticleId) -> Result<(), ArticleGatewayError>;
}


pub trait ArticleRater {
    async fn rate_article(&self, article_id: &ArticleId, user_id: &UserId) -> Result<bool, ArticleGatewayError>;
    async fn unrate_article(&self, article_id: &ArticleId, user_id: &UserId) -> Result<bool, ArticleGatewayError>;
    async fn is_user_rated_article(article_id: &ArticleId, user_id: &UserId) -> Result<bool, ArticleGatewayError>;
    async fn is_user_rated_articles(
        &self,
        article_ids: &[ArticleId],
        user_id: &UserId,
    ) -> Result<Vec<bool>, ArticleGatewayError>;
}

pub trait ArticleGateway: ArticleReader + ArticleWriter + ArticleRemover + ArticleRater {}
