use crate::application::common::{
    article_gateway::ArticleGateway,
    error::AppError,
    file_map_gateway::FileMapReader,
    file_storage_gateway::FileStorageLinker,
    id_provider::IdProvider,
    interactor::Interactor
};
use crate::domain::models::rate_state::RateState;
use crate::domain::{
    models::{
        article::ArticleId,
        article_state::ArticleState,
        file::FileId,
        tag::Tag,
        user_id::UserId
    },
    services::access::ensure_can_get_article
};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use utoipa::{IntoParams, ToSchema};

#[derive(Deserialize, IntoParams)]
pub struct GetArticleInput {
    #[param(example = uuid::Uuid::new_v4, value_type=uuid::Uuid)]
    pub id: ArticleId
}

#[derive(Serialize, ToSchema)]
pub struct ArticleFile {
    #[schema(example = uuid::Uuid::new_v4, value_type=uuid::Uuid)]
    pub id: FileId,
    #[schema(example = "example.png")]
    pub filename: String,
    #[schema(example = "image/png")]
    pub content_type: String,
    #[schema(example = "https://s3.example.com/article-assets/987e9dc9-d84c-4ba7-837f-db755a0fdc55/80bbc0bc-4064-420a-b4ed-4f94b4575321")]
    pub url: String,
    
    pub created_at: DateTime<Utc>,
    pub updated_at: Option<DateTime<Utc>>,
}

#[derive(Serialize, ToSchema)]
pub struct GetArticleOutput {
    #[schema(example = "Super rust tips")]
    pub title: String,
    #[schema(example = uuid::Uuid::new_v4, value_type=Option<uuid::Uuid>)]
    pub poster: Option<FileId>,
    #[schema(example = "In this article, we will explore some of the best practices in Rust programming...")]
    pub content: String, // todo: server rendering 
    pub state: ArticleState,
    #[schema(example = 100)]
    pub views: u32,
    #[schema(example = -5)]
    pub rating: i64,
    #[schema(example = uuid::Uuid::new_v4, value_type=uuid::Uuid)]
    pub author_id: UserId,
    #[schema(example = json!(vec!["rust", "programming", "tips"]), value_type = Vec<String>)]
    pub tags: Vec<Tag>,
    
    pub self_rate: RateState,
    pub files: Vec<ArticleFile>,

    pub created_at: DateTime<Utc>,
    pub updated_at: Option<DateTime<Utc>>
}

pub struct GetArticle<'interactor> {
    pub id_provider: Box<dyn IdProvider>,
    pub article_gateway: &'interactor dyn ArticleGateway,
    pub file_map_reader: &'interactor dyn FileMapReader,
    pub file_storage_linker: &'interactor dyn FileStorageLinker,
}

impl Interactor<GetArticleInput, GetArticleOutput> for GetArticle<'_> {
    async fn execute(&self, input: GetArticleInput) -> Result<GetArticleOutput, AppError> {
        let article = match self.article_gateway.get_article(&input.id).await? {
            Some(article) => article,
            None => return Err(AppError::NotFound("id".into()))
        };

        ensure_can_get_article(
            self.id_provider.permissions(),
            self.id_provider.user_state(),
            &article.state,
            &article.author_id,
            self.id_provider.user_id(),
        )?;
        
        let (self_rate, files, inc_res) = tokio::join!(
            self.article_gateway.user_rate_state(&article.id, self.id_provider.user_id()),
            self.file_map_reader.get_article_files(&article.id),
            self.article_gateway.increment_article_views(&article.id)
        );
        
        inc_res?;
        
        Ok(GetArticleOutput {
            title: article.title,
            poster: article.poster,
            content: article.content,
            state: article.state,
            views: article.views,
            rating: article.rating,
            author_id: article.author_id,
            tags: article.tags,

            self_rate: self_rate?,
            files: files?.into_iter().filter(|f| f.is_uploaded).map(|file| {
                ArticleFile {
                    id: file.id,
                    filename: file.filename,
                    content_type: file.content_type,
                    url: self.file_storage_linker.download_link(&article.id, &file.id),
                    created_at: file.created_at,
                    updated_at: file.updated_at
                }
            }).collect(),
            
            created_at: article.created_at,
            updated_at: article.updated_at
        })
    }
}
