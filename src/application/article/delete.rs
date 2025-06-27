use serde::Deserialize;
use utoipa::IntoParams;
use crate::application::common::{
    error::AppError,
    comment_gateway::CommentRemover,
    article_gateway::ArticleGateway,
    id_provider::IdProvider,
    interactor::Interactor
};
use crate::domain::{
    models::article::ArticleId,
    services::access::ensure_can_delete_article
};

#[derive(Deserialize, IntoParams)]
pub struct DeleteArticleInput {
    #[param(example = uuid::Uuid::new_v4, value_type=uuid::Uuid)]
    pub id: ArticleId
}

pub struct DeleteArticle<'interactor> {
    pub id_provider: Box<dyn IdProvider>,
    pub article_gateway: &'interactor dyn ArticleGateway,
    pub comment_remover: &'interactor dyn CommentRemover
}

impl Interactor<DeleteArticleInput, ()> for DeleteArticle<'_> {
    async fn execute(&self, input: DeleteArticleInput) -> Result<(), AppError> {
        let article_author_id = match self.article_gateway.get_article_author(&input.id).await? {
            Some(author_id) => author_id,
            None => return Err(AppError::NotFound("id".into()))
        };
        
        ensure_can_delete_article(
            self.id_provider.permissions(),
            self.id_provider.user_state(),
            self.id_provider.user_id(),
            &article_author_id
        )?;
        
        let (res1, res2) = tokio::join!(
            self.article_gateway.remove(&input.id),
            self.comment_remover.remove_by_article(&input.id)
        );
        res1?;
        res2?;

        Ok(())
    }
}
