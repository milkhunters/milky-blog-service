use crate::application::common::{
    article_gateway::ArticleGateway,
    error::AppError,
    file_map_gateway::FileMapReader,
    file_storage_gateway::FileStorageLinker,
    id_provider::IdProvider,
    interactor::Interactor
};
use crate::domain::models::tag::TagId;
use crate::domain::{
    models::{
        article::ArticleId,
        article_state::ArticleState,
        tag::Tag,
        user_id::UserId,
        rate_state::RateState
    },
    services::access::ensure_can_find_articles
};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

#[derive(Deserialize)]
pub enum OrderBy {
    CreatedAtDesc,
    CreatedAtAsc,
    ViewsDesc,
    ViewsAsc,
    RatingDesc,
    RatingAsc
}

#[derive(Deserialize)]
pub struct FindArticleInput {
    pub page: u32,
    pub per_page: u8,
    pub query: Option<String>,
    pub tags: Vec<TagId>,
    pub order_by: OrderBy,
    pub state: ArticleState,
    pub author_id: Option<UserId>,
}

#[derive(Serialize)]
pub struct ArticleItem {
    pub id: ArticleId,
    pub title: String,
    pub poster_url: Option<String>,
    pub state: ArticleState,
    pub views: u32,
    pub rating: i64,
    pub author_id: UserId,
    pub tags: Vec<Tag>,

    pub self_rate: RateState,

    pub created_at: DateTime<Utc>,
    pub updated_at: Option<DateTime<Utc>>
}

pub type FindArticleOutput = Vec<ArticleItem>;

pub struct FindArticle<'interactor> {
    id_provider: &'interactor dyn IdProvider,
    article_gateway: &'interactor dyn ArticleGateway,
    file_map_reader: &'interactor dyn FileMapReader,
    file_storage_linker: &'interactor dyn FileStorageLinker,
}

impl Interactor<FindArticleInput, FindArticleOutput> for FindArticle<'_> {
    async fn execute(&self, input: FindArticleInput) -> Result<FindArticleOutput, AppError> {
        ensure_can_find_articles(
            self.id_provider.permissions(),
            self.id_provider.user_state(),
            &input.state,
            &input.author_id,
            self.id_provider.user_id(),
        )?;
        
        let articles = self.article_gateway.find_articles(
            input.query,
            input.per_page,
            (input.page - 1).wrapping_mul(input.per_page as u32),
            &input.order_by,
            &input.state,
            &input.tags,
            &input.author_id
        ).await?;

        let rates = self.article_gateway.user_rate_states(
            &articles.iter().map(|item| item.id).collect::<Vec<_>>(),
            self.id_provider.user_id()
        ).await?;

        if articles.len() != rates.len() {
            return Err(AppError::Critical(format!(
                "article count({}) does not match rating count({})", 
                articles.len(), rates.len()
            )));
        }

        Ok(articles.into_iter().zip(rates.into_iter()).map(|(article, self_rate)| {
            ArticleItem {
                id: article.id,
                title: article.title,
                poster_url: article.poster.map(|poster| self.file_storage_linker.download_link(&article.id, &poster)),
                state: article.state,
                views: article.views,
                rating: article.rating,
                author_id: article.author_id,
                tags: article.tags,
                self_rate,
                created_at: article.created_at,
                updated_at: article.updated_at
            }
        }).collect::<FindArticleOutput>())
    }
}
