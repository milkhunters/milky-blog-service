use serde::{Deserialize, Serialize};

#[derive(PartialEq, Debug, Serialize, Deserialize)]
pub enum ArticleState {
    Draft,
    Published,
    Archived
}
