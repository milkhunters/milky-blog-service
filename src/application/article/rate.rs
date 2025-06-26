use crate::application::common::article_gateway::ArticleGateway;
use crate::application::common::{
    article_gateway::{ArticleRater, ArticleReader},
    error::AppError,
    id_provider::IdProvider,
    interactor::Interactor
};
use crate::domain::{
    models::{
        article::ArticleId,
        rate_state::RateState
    },
    services::access::ensure_can_rate_article
};

pub struct RateArticleInput {
    pub id: ArticleId,
    pub state: RateState
}

pub struct RateArticle<'interactor> {
    pub id_provider: Box<dyn IdProvider>,
    pub article_gateway: &'interactor dyn ArticleGateway
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
