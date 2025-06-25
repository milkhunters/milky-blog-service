use crate::application::common::{
    article_gateway::ArticleGateway,
    error::AppError,
    file_map_gateway::FileMapReader,
    file_storage_gateway::FileStorageLinker,
    id_provider::IdProvider,
    interactor::Interactor
};
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
use crate::domain::models::rate_state::RateState;

#[derive(Deserialize)]
pub struct GetArticleInput {
    pub id: ArticleId
}

#[derive(Serialize)]
pub struct ArticleFile {
    pub id: FileId,
    pub filename: String,
    pub content_type: String,
    pub url: String,
    
    pub created_at: DateTime<Utc>,
    pub updated_at: Option<DateTime<Utc>>,
}

#[derive(Serialize)]
pub struct GetArticleOutput {
    pub title: String,
    pub poster: Option<FileId>,
    pub content: String, // todo: server rendering 
    pub state: ArticleState,
    pub views: u32,
    pub rating: i64,
    pub author_id: UserId,
    pub tags: Vec<Tag>,
    
    pub self_rate: RateState,
    pub files: Vec<ArticleFile>,

    pub created_at: DateTime<Utc>,
    pub updated_at: Option<DateTime<Utc>>
}

pub struct GetArticle<'interactor> {
    id_provider: &'interactor dyn IdProvider,
    article_gateway: &'interactor dyn ArticleGateway,
    file_map_reader: &'interactor dyn FileMapReader,
    file_storage_linker: &'interactor dyn FileStorageLinker,
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
            files: files?.into_iter().map(|file| {
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
