use crate::application::common::{
    article_gateway::ArticleGateway,
    error::AppError,
    file_storage_gateway::FileStorageLinker,
    id_provider::IdProvider,
    interactor::Interactor
};
use crate::domain::{
    models::{
        article::ArticleId,
        article_state::ArticleState,
        rate_state::RateState,
        tag::Tag,
        user_id::UserId
    },
    error::{DomainError, ValidationError},
    services::{
        access::ensure_can_find_articles,
        validator::{validate_article_tags, validate_page, validate_per_page}
    }
};
use chrono::{DateTime, Utc};
use serde::{de, Deserialize, Serialize};
use std::collections::HashMap;
use std::fmt;
use utoipa::{IntoParams, ToSchema};

#[derive(PartialEq, Debug, Serialize, Deserialize, ToSchema)]
pub enum FindArticleOrderBy {
    /// Order by the number of views in descending order
    CreatedAtDesc,
    /// Order by the number of views in ascending order
    CreatedAtAsc,
    /// Order by the number of views in descending order
    ViewsDesc,
    /// Order by the number of views in ascending order
    ViewsAsc,
    /// Order by the rating in descending order
    RatingDesc,
    /// Order by the rating in ascending order
    RatingAsc
}

#[derive(Deserialize, IntoParams)]
pub struct FindArticleInput {
    #[param(example = 1, default = 1)]
    pub page: u32,
    #[param(example = 10, default = 10)]
    pub per_page: u8,
    pub query: Option<String>, // todo validate query length
    #[param(example = json!(vec!["js".to_string()]), value_type = Vec<String>)]
    #[serde(deserialize_with = "deserialize_str_list", default)]
    pub tags: Vec<String>,
    pub state: ArticleState,
    #[param(example = "CreatedAtDesc", value_type = String)]
    pub order_by: FindArticleOrderBy,
    #[param(example = uuid::Uuid::new_v4, value_type = Option<uuid::Uuid>)]
    pub author_id: Option<UserId>,
}

#[derive(Serialize, ToSchema)]
pub struct ArticleItem {
    #[schema(example = uuid::Uuid::new_v4, value_type=uuid::Uuid)]
    pub id: ArticleId,
    #[schema(example = "Super javascript tips")]
    pub title: String,
    #[schema(example = "https://s3.example.com/article-assets/987e9dc9-d84c-4ba7-837f-db755a0fdc55/80bbc0bc-4064-420a-b4ed-4f94b4575321")]
    pub poster_url: Option<String>,
    pub state: ArticleState,
    #[schema(example = 100)]
    pub views: u32,
    #[schema(example = 97)]
    pub rating: i64,
    #[schema(example = uuid::Uuid::new_v4, value_type=uuid::Uuid)]
    pub author_id: UserId,
    #[schema(value_type = Vec<Tag>)]
    pub tags: Vec<Tag>,

    pub self_rate: RateState,

    pub created_at: DateTime<Utc>,
    pub updated_at: Option<DateTime<Utc>>
}

#[derive(Serialize, ToSchema)]
pub struct FindArticleOutput(pub Vec<ArticleItem>);

pub struct FindArticle<'interactor> {
    pub id_provider: Box<dyn IdProvider>,
    pub article_gateway: &'interactor dyn ArticleGateway,
    pub file_storage_linker: &'interactor dyn FileStorageLinker,
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

        let mut validation_err_map = HashMap::<String, ValidationError>::new();
        if let Err(DomainError::Validation((key, err))) = validate_page(input.page) {
            validation_err_map.insert(key, err);
        }
        if let Err(DomainError::Validation((key, err))) = validate_per_page(input.per_page) {
            validation_err_map.insert(key, err);
        }
        if let Err(DomainError::Validation((key, val))) = validate_article_tags(&input.tags) {
            validation_err_map.insert(key, val);
        }

        if !validation_err_map.is_empty() {
            return Err(AppError::Validation(validation_err_map));
        }
        
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

        Ok(FindArticleOutput(articles.into_iter().zip(rates.into_iter()).map(|(article, self_rate)| {
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
        }).collect::<Vec<_>>()))
    }
}

pub fn deserialize_str_list<'de, D>(deserializer: D) -> Result<Vec<String>, D::Error>
where
    D: de::Deserializer<'de>,
{
    struct StringVecVisitor;

    impl<'de> de::Visitor<'de> for StringVecVisitor {
        type Value = Vec<String>;

        fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
            formatter.write_str("a string containing a list of Strings")
        }

        fn visit_str<E>(self, v: &str) -> Result<Self::Value, E>
        where
            E: de::Error,
        {
            Ok(
                v.split(";")
                    .map(|s| s.trim().to_string())
                    .collect::<Vec<_>>()
            )
        }

        fn visit_none<E>(self) -> Result<Self::Value, E>
        where
            E: de::Error,
        {
            Ok(Vec::new())
        }
    }

    deserializer.deserialize_any(StringVecVisitor)
}