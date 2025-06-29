use serde::Deserialize;
use utoipa::IntoParams;
use crate::application::common::{
    article_gateway::ArticleReader,
    error::AppError,
    file_map_gateway::FileMapGateway,
    file_storage_gateway::FileStorageReader,
    id_provider::IdProvider,
    interactor::Interactor
};
use crate::domain::{
    models::file::FileId,
    services::access::ensure_can_update_article
};

#[derive(Deserialize, IntoParams)]
pub struct ConfirmArticleFileInput {
    #[param(example = uuid::Uuid::new_v4, value_type=uuid::Uuid)]
    pub id: FileId
}

pub struct ConfirmArticleFile<'interactor> {
    pub id_provider: Box<dyn IdProvider>,
    pub article_reader: &'interactor dyn ArticleReader,
    pub file_map_gateway: &'interactor dyn FileMapGateway,
    pub file_storage_reader: &'interactor dyn FileStorageReader,
}

impl Interactor<ConfirmArticleFileInput, ()> for ConfirmArticleFile<'_> {
    async fn execute(&self, input: ConfirmArticleFileInput) -> Result<(), AppError> {
        let mut file = self.file_map_gateway.get_file(&input.id).await?
            .ok_or(AppError::NotFound("id".into()))?;
        
        let article_author = match self.article_reader.get_article_author(&file.article_id).await? {
            Some(author_id) => author_id,
            None => return Err(AppError::Critical("ConfirmArticleFile file exists but article not found".into()))
        };

        ensure_can_update_article(
            self.id_provider.permissions(),
            self.id_provider.user_state(),
            self.id_provider.user_id(),
            &article_author
        )?;
        
        self.file_storage_reader.is_exist_file(
            &file.article_id,
            &file.id
        ).await?
            .then(|| ())
            .ok_or(AppError::NotFound("id".into()))?;
        
        file.mark_uploaded();
        
        self.file_map_gateway.save(&file).await?;
        
        Ok(())
    }
}
