use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

#[derive(Deserialize, Serialize, ToSchema)]
#[serde(rename_all = "lowercase")]
pub enum RateState {
    Up,
    Neutral,
    Down
}
