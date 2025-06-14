

pub type TagId = uuid::Uuid;
pub const TAG_TITLE_MAX: usize = 64;
pub const TAG_TITLE_MIN: usize = 1;

pub struct Tag {
    pub id: TagId,
    pub title: String
}

impl Tag {
    pub fn new(title: String) -> Self {
        if title.len() > TAG_TITLE_MAX {
            panic!("Tag title exceeds maximum length of {}", TAG_TITLE_MAX);
        }
        if title.len() < TAG_TITLE_MIN {
            panic!("Tag title must be at least {} characters long", TAG_TITLE_MIN);
        }
        Self { id: TagId::new_v4(), title }
    }
}