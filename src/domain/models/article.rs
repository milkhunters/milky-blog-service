use chrono::{DateTime, Utc};
use crate::domain::models::{
    article_state::ArticleState,
    file::FileId,
    user_id::UserId
};

pub type ArticleId = uuid::Uuid;
pub const ARTICLE_TITLE_MAX: usize = 255;
pub const ARTICLE_TITLE_MIN: usize = 1;

pub struct Article {
    pub id: ArticleId,
    pub title: String,
    pub poster: Option<FileId>,
    pub content: String,
    pub state: ArticleState,
    pub views: u32,
    pub tags: Vec<String>,
    pub author_id: UserId,

    pub created_at: DateTime<Utc>,
    pub updated_at: Option<DateTime<Utc>>
}

impl Article {
    pub fn new(
        title: String,
        poster: Option<FileId>,
        content: String,
        author_id: UserId,
        tags: Vec<String>
    ) -> Self {
        if title.len() > ARTICLE_TITLE_MAX {
            panic!("Article title exceeds maximum length of {}", ARTICLE_TITLE_MAX);
        }
        if title.len() < ARTICLE_TITLE_MIN {
            panic!("Article title must be at least {} characters long", ARTICLE_TITLE_MIN);
        }
        Self {
            id: ArticleId::new_v4(),
            title,
            poster,
            content,
            state: ArticleState::Draft,
            views: 0,
            tags,
            author_id,
            created_at: Utc::now(),
            updated_at: None
        }
    }

    pub fn update(&mut self, new_content: String) {
        self.content = new_content;
        self.updated_at = Some(Utc::now());
    }

    pub fn mark_published(&mut self) {
        self.state = ArticleState::Published;
        self.updated_at = Some(Utc::now());
    }
}