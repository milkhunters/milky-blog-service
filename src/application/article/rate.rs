use crate::application::common::{
    error::AppError,
    article_gateway::{ArticleRater, ArticleReader},
    id_provider::IdProvider,
    interactor::Interactor
};
use crate::domain::{
    services::access::ensure_can_rate_article,
    models::{
        rate_state::RateState,
        article::ArticleId
    }
};
use async_trait::async_trait;

#[async_trait]
pub trait ArticleReaderRaterGateway: ArticleReader + ArticleRater {}

pub struct RateArticleInput {
    pub id: ArticleId,
    pub state: RateState
}

pub struct RateArticle<'interactor> {
    id_provider: &'interactor dyn IdProvider,
    article_gateway: &'interactor dyn ArticleReaderRaterGateway
} 

impl Interactor<RateArticleInput, ()> for RateArticle<'_> {
    async fn execute(&self, input: RateArticleInput) -> Result<(), AppError> {
        let article = match self.article_gateway.get_article(&input.id).await? {
            Some(article) => article,
            None => return Err(AppError::NotFound("id".into()))
        };

        ensure_can_rate_article(
            self.id_provider.permissions(),
            self.id_provider.user_state(),
            &article.state,
        )?;

        self.article_gateway.rate_article(&article.id, self.id_provider.user_id(), &input.state).await?;
        Ok(())
    }
}
