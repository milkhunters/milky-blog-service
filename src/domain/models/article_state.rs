use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

#[derive(PartialEq, Debug, Serialize, Deserialize, ToSchema)]
pub enum ArticleState {
    /// When the article is in the process of being written 
    Draft,
    /// When the article is ready to be read by others
    Published,
    /// When the article is no longer available for reading
    Archived
}
