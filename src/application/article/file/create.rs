use std::collections::HashMap;
use serde::Deserialize;
use utoipa::ToSchema;
use crate::application::common::{
    article_gateway::ArticleReader,
    error::AppError,
    file_map_gateway::FileMapGateway,
    file_storage_gateway::FileStorageLinker,
    presigned_url::PreSignedUrl,
    id_provider::IdProvider,
    interactor::Interactor
};
use crate::domain::{
    models::{
        article::ArticleId,
        file::{File, CONTENT_LENGTH_RANGE, FILE_UPLOAD_TTL}
    },
    services::{
        access::ensure_can_update_article,
        validator::{
            validate_filename,
            validate_mime_content_type
        }
    }
};
use crate::domain::error::{DomainError, ValidationError};

#[derive(Deserialize, ToSchema)]
pub struct CreateArticleFileInput {
    #[schema(example = uuid::Uuid::new_v4, value_type=uuid::Uuid)]
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
            None => return Err(AppError::NotFound("article_id".into()))
        };

        ensure_can_update_article(
            self.id_provider.permissions(),
            self.id_provider.user_state(),
            self.id_provider.user_id(),
            &article_author
        )?;
        
        let mut validation_errors = HashMap::<String, ValidationError>::new();
        if let Err(DomainError::Validation((key, val))) = validate_filename(&input.filename) {
            validation_errors.insert(key, val);
        }
        if let Err(DomainError::Validation((key, val))) = validate_mime_content_type(&input.content_type) {
            validation_errors.insert(key, val);
        }
        if !validation_errors.is_empty() {
            return Err(AppError::Validation(validation_errors));
        }
        
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
                FILE_UPLOAD_TTL
            )
        );
        
        res?;
        Ok(url?)
    }
}
