use chrono::{DateTime, Utc};
use crate::domain::models::{
    article_state::ArticleState,
    file::FileId,
    user_id::UserId
};

pub type ArticleId = uuid::Uuid;
pub const ARTICLE_TITLE_MAX: usize = 255;
pub const ARTICLE_TITLE_MIN: usize = 1;
pub const ARTICLE_CONTENT_MAX: usize = 32000;

pub struct Article {
    pub id: ArticleId,
    pub title: String,
    pub poster: Option<FileId>,
    pub content: String,
    pub state: ArticleState,
    pub views: u32,
    pub author_id: UserId,

    pub created_at: DateTime<Utc>,
    pub updated_at: Option<DateTime<Utc>>
}

impl Article {
    pub fn new(
        title: String,
        poster: Option<FileId>,
        content: String,
        author_id: UserId
    ) -> Self {
        Self {
            id: ArticleId::new_v4(),
            title,
            poster,
            content,
            state: ArticleState::Draft,
            views: 0,
            author_id,
            created_at: Utc::now(),
            updated_at: None
        }
    }

    pub fn update(
        &mut self,
        title: String,
        poster: Option<FileId>,
        content: String,
        state: ArticleState,
    ) {
        self.title = title;
        self.poster = poster;
        self.content = content;
        self.state = state;
        self.updated_at = Some(Utc::now());
    }
    
    pub fn increment_views(&mut self) {
        self.views += 1;
    }
}
