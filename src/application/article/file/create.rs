use crate::application::common::{
    article_gateway::ArticleReader,
    error::{AppError, ErrorContent},
    file_map_gateway::FileMapGateway,
    file_storage_gateway::FileStorageLinker,
    presigned_url::PreSignedUrl,
    id_provider::IdProvider,
    interactor::Interactor
};
use crate::domain::{
    models::{
        article::ArticleId,
        file::{File, CONTENT_LENGTH_RANGE, FILE_UPLOAD_EXPIRATION}
    },
    services::access::ensure_can_update_article
};


pub struct CreateArticleFileInput {
    pub article_id: ArticleId,
    pub filename: String,
    pub content_type: String
}

pub type CreateArticleFileOutput = PreSignedUrl;

pub struct CreateArticleFile<'interactor> {
    id_provider: &'interactor dyn IdProvider,
    article_reader: &'interactor dyn ArticleReader,
    file_map_gateway: &'interactor dyn FileMapGateway,
    file_storage_linker: &'interactor dyn FileStorageLinker,
}

impl Interactor<CreateArticleFileInput, CreateArticleFileOutput> for CreateArticleFile<'_> {
    async fn execute(&self, input: CreateArticleFileInput) -> Result<CreateArticleFileOutput, AppError> {
        let article_author = match self.article_reader.get_article_author(&input.article_id).await? {
            Some(author_id) => author_id,
            None => return Err(AppError::NotFound(ErrorContent::Message("article not found".into())))
        };

        ensure_can_update_article(
            self.id_provider.permissions(),
            self.id_provider.user_state(),
            self.id_provider.user_id(),
            &article_author
        )?;
        
        let file = File::new(
            input.filename,
            input.content_type,
            input.article_id
        );
        
        let (res, url) = tokio::join!(
            self.file_map_gateway.save(&file),
            self.file_storage_linker.upload_link(
                &file.article_id,
                &file.id,
                &file.content_type,
                CONTENT_LENGTH_RANGE,
                FILE_UPLOAD_EXPIRATION
            )
        );
        
        res?;
        Ok(url?)
    }
}
