use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

#[derive(PartialEq, Deserialize, Serialize, ToSchema)]
pub enum CommentState {
    Deleted,
    Published
}