use serde::{Deserialize, Serialize};

#[derive(PartialEq, Serialize, Deserialize)]
pub enum UserState {
    Active,
    NotVerify,
    Banned,
    Deleted,
}
