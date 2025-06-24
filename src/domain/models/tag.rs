use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

pub type TagId = uuid::Uuid;
pub const TAG_TITLE_MAX: usize = 64;
pub const TAG_TITLE_MIN: usize = 2;

#[derive(Serialize, Deserialize)]
pub struct Tag {
    pub id: TagId,
    pub title: String,
    pub created_at: DateTime<Utc>,
}

impl Tag {
    pub fn new(title: String) -> Self {
        Self { id: TagId::new_v4(), title, created_at: Utc::now() }
    }
}