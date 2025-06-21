use chrono::{DateTime, Utc};
use crate::domain::models::{
    article::ArticleId,
    comment_state::CommentState,
    user_id::UserId
};

pub type CommentId = uuid::Uuid;
pub const COMMENT_CONTENT_MAX: usize = 1000;

pub struct Comment {
    pub id: CommentId,
    pub content: String,
    pub author_id: UserId,
    pub article_id: ArticleId,
    pub parent_id: Option<CommentId>,
    pub rating: i64,
    pub state: CommentState,

    pub created_at: DateTime<Utc>,
    pub updated_at: Option<DateTime<Utc>>,
}

impl Comment {
    pub fn new(content: String, author_id: UserId, article_id: ArticleId, parent_id: Option<CommentId>) -> Self {
        Self {
            id: CommentId::new_v4(),
            content,
            author_id,
            article_id,
            parent_id,
            rating: 0,
            state: CommentState::Published,
            created_at: Utc::now(),
            updated_at: None,
        }
    }

    pub fn update(&mut self, new_content: String) {
        self.content = new_content;
        self.updated_at = Some(Utc::now());
    }
    
    pub fn mark_deleted(&mut self) {
        self.state = CommentState::Deleted;
        self.updated_at = Some(Utc::now());
    }
}