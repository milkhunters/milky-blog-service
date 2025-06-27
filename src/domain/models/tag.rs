use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

pub type TagId = uuid::Uuid;
pub const TAG_TITLE_MAX: usize = 64;
pub const TAG_TITLE_MIN: usize = 2;

#[derive(Serialize, Deserialize, ToSchema)]
pub struct Tag {
    #[schema(example = uuid::Uuid::new_v4, value_type=uuid::Uuid)]
    pub id: TagId,
    #[schema(example = "rust", max_length = 64, min_length = 2)]
    pub title: String,
    pub created_at: DateTime<Utc>,
}

impl Tag {
    pub fn new(title: String) -> Self {
        Self { id: TagId::new_v4(), title, created_at: Utc::now() }
    }
}