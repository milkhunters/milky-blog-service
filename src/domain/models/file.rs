use chrono::{DateTime, Utc};
use once_cell::sync::Lazy;
use regex::Regex;

pub type FileId = uuid::Uuid;
pub const FILE_NAME_MAX: usize = 255;
pub const FILE_MIME_TYPE_MAX: usize = 255; // RFC 4288 and RFC 6838
pub static FILE_MIME_TYPE_REGEX: Lazy<Regex> = Lazy::new(|| Regex::new(r"\w+/[-+.\w]+").expect("Invalid MIME type regex"));


pub struct File {
    pub id: FileId,
    pub filename: String,
    pub content_type: String,
    pub is_uploaded: bool,

    pub created_at: DateTime<Utc>,
    pub updated_at: Option<DateTime<Utc>>,
}

impl File {
    pub fn new(filename: String, content_type: String) -> Self {
        Self {
            id: FileId::new_v4(),
            filename,
            content_type,
            is_uploaded: false,
            created_at: Utc::now(),
            updated_at: None,
        }
    }

    pub fn mark_uploaded(&mut self) {
        self.is_uploaded = true;
        self.updated_at = Some(Utc::now());
    }
}
