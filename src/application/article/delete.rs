use crate::application::common::{
    error::{AppError, ErrorContent},
    comment_gateway::CommentRemover,
    article_gateway::ArticleGateway,
    id_provider::IdProvider,
    interactor::Interactor
};
use crate::domain::{
    models::article::ArticleId,
    services::access::ensure_can_delete_article
};

pub struct DeleteArticleInput {
    pub id: ArticleId
}

pub struct DeleteArticle<'interactor> {
    id_provider: &'interactor dyn IdProvider,
    article_gateway: &'interactor dyn ArticleGateway,
    comment_remover: &'interactor dyn CommentRemover
}

impl Interactor<DeleteArticleInput, ()> for DeleteArticle<'_> {
    async fn execute(&self, input: DeleteArticleInput) -> Result<(), AppError> {
        let article_author_id = match self.article_gateway.get_article_author_id(&input.id).await? {
            Some(author_id) => author_id,
            None => return Err(AppError::NotFound(ErrorContent::Message("article not found".into())))
        };
        
        ensure_can_delete_article(
            self.id_provider.permissions(),
            self.id_provider.user_state(),
            self.id_provider.user_id(),
            &article_author_id
        )?;
        
        let (res1, res2) = tokio::join!(
            self.article_gateway.remove_article(&input.id),
            self.comment_remover.remove_article_comments(&input.id)
        );
        res1?;
        res2?;

        Ok(())
    }
}
