use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

pub const TAG_TITLE_MAX: usize = 64;
pub const TAG_TITLE_MIN: usize = 2;

#[derive(Serialize, Deserialize, ToSchema)]
pub struct Tag {
    #[schema(example = "rust", max_length = 64, min_length = 2)]
    pub title: String,
    pub created_at: DateTime<Utc>
}

impl Tag {
    pub fn new(title: String) -> Self {
        Self { title, created_at: Utc::now() }
    }
}
