use crate::application::common::{
    article_gateway::ArticleReader,
    error::AppError,
    file_map_gateway::FileMapGateway,
    file_storage_gateway::FileStorageRemover,
    id_provider::IdProvider,
    interactor::Interactor
};
use crate::domain::models::file::FileId;
use crate::domain::services::access::ensure_can_update_article;
use serde::Deserialize;
use utoipa::IntoParams;

#[derive(Deserialize, IntoParams)]
pub struct DeleteArticleFileInput {
    #[param(example = uuid::Uuid::new_v4, value_type=uuid::Uuid)]
    pub id: FileId
}

pub struct DeleteArticleFile<'interactor> {
    pub id_provider: Box<dyn IdProvider>,
    pub article_reader: &'interactor dyn ArticleReader,
    pub file_map_gateway: &'interactor dyn FileMapGateway,
    pub file_storage_remover: &'interactor dyn FileStorageRemover,
}

impl Interactor<DeleteArticleFileInput, ()> for DeleteArticleFile<'_> {
    async fn execute(&self, input: DeleteArticleFileInput) -> Result<(), AppError> {
        let file = self.file_map_gateway.get_file(&input.id).await?
            .ok_or(AppError::NotFound("id".into()))?;
        
        let article_author = match self.article_reader.get_article_author(&file.article_id).await? {
            Some(author_id) => author_id,
            None => return Err(AppError::Critical("DeleteArticleFile file exists but article not found".into()))
        };

        ensure_can_update_article(
            self.id_provider.permissions(),
            self.id_provider.user_state(),
            self.id_provider.user_id(),
            &article_author
        )?;
        
        let rem_file_map_fut = self.file_map_gateway.remove(&file.id);
        let rem_file_storage_fut = self.file_storage_remover.remove(
            &file.article_id,
            &file.id
        );
        
        if file.is_uploaded {
            let (res1, res2) = tokio::join!(
                rem_file_map_fut,
                rem_file_storage_fut
            );
            res1?;
            res2?;
        } else {
            rem_file_map_fut.await?;
        }
        
        Ok(())
    }
}
