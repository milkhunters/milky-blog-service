use std::collections::HashMap;
use async_trait::async_trait;
use crate::application::common::{
    article_gateway::ArticleReader,
    comment_gateway::{
        CommentReader,
        CommentRater
    },
    error::AppError,
    id_provider::IdProvider,
    interactor::Interactor
};
use crate::domain::{
    models::{
        article::ArticleId,
        comment::CommentId,
        comment_state::CommentState,
        user_id::UserId
    },
    services::access::ensure_can_get_comments
};
use chrono::{DateTime, Utc};
use crate::domain::models::permissions::Permission::GetAnyComment;

pub struct GetCommentsTreeInput {
    pub article_id: ArticleId
}

pub struct GetCommentsTreeItem {
    pub id: CommentId,
    pub content: String,
    pub author_id: UserId,
    pub article_id: ArticleId,
    pub parent_id: Option<CommentId>,
    pub children: Vec<GetCommentsTreeItem>,
    pub rating: i64,
    pub state: CommentState,
    pub level: u32,
    pub is_self_rated: bool,
    
    pub created_at: DateTime<Utc>,
    pub updated_at: Option<DateTime<Utc>>,

}

pub type GetCommentsTreeOutput = Vec<GetCommentsTreeItem>;


#[async_trait]
pub trait CommentReaderRaterGateway: CommentReader + CommentRater {}


pub struct GetCommentsTree<'interactor> {
    id_provider: &'interactor dyn IdProvider,
    comment_gateway: &'interactor dyn CommentReaderRaterGateway,
    article_reader: &'interactor dyn ArticleReader,
}

impl Interactor<GetCommentsTreeInput, GetCommentsTreeOutput> for GetCommentsTree<'_> {
    async fn execute(&self, input: GetCommentsTreeInput) -> Result<GetCommentsTreeOutput, AppError> {
        let article_state = self.article_reader
            .get_article_state(&input.article_id)
            .await?
            .ok_or(AppError::NotFound("article_id".into()))?;

        ensure_can_get_comments(
            self.id_provider.permissions(),
            self.id_provider.user_state(),
            &article_state
        )?;
        
        
        let comments = self.comment_gateway.get_comments(&input.article_id).await?;
        let rated = self.comment_gateway.is_user_rate_comments(
                &comments.iter().map(|(c, _)| c.id).collect::<Vec<_>>(), 
                self.id_provider.user_id()
        ).await?;
        
        if comments.len() != rated.len() {
            return Err(AppError::Critical(format!(
                "GetCommentsTree rated comments count mismatch ({} != {})",
                rated.len(),
                comments.len()
            ).into()));
        }
        
        let can_look_deleted = self.id_provider.permissions().contains(&GetAnyComment);
        let comment_rows = comments.into_iter().zip(rated.into_iter())
            .map(|((comment, level), is_self_rated)| {
                GetCommentsTreeItem {
                    id: comment.id,
                    content: match comment.state {
                        CommentState::Published => comment.content,
                        CommentState::Deleted if can_look_deleted => comment.content,
                        CommentState::Deleted => "this comment has been deleted".into(),
                    },
                    author_id: comment.author_id,
                    article_id: comment.article_id,
                    parent_id: comment.parent_id,
                    children: vec![],
                    rating: comment.rating,
                    state: comment.state,
                    level,
                    is_self_rated,
                    created_at: comment.created_at,
                    updated_at: comment.updated_at
                }
            })
            .collect::<Vec<_>>();
        
        let mut map: HashMap<Option<CommentId>, Vec<GetCommentsTreeItem>> = HashMap::new();
        for comment in comment_rows {
            map.entry(comment.parent_id).or_default().push(comment);
        }

        fn attach_children(
            parent: &mut GetCommentsTreeItem,
            map: &mut HashMap<Option<CommentId>, Vec<GetCommentsTreeItem>>
        ) {
            if let Some(mut kids) = map.remove(&Some(parent.id)) {
                for kid in &mut kids {
                    attach_children(kid, map);
                }
                parent.children = kids;
            }
        }

        let mut roots = map.remove(&None).unwrap_or_default(); // todo sort by created_at
        for root in &mut roots {
            attach_children(root, &mut map); // todo check max recursion depth
        }
        Ok(roots)
    }
}
