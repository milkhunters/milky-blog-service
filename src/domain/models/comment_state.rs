use serde::{Deserialize, Serialize};

#[derive(PartialEq, Deserialize, Serialize)]
pub enum CommentState {
    Deleted,
    Published
}