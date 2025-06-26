use serde::Serialize;
use utoipa::ToSchema;

#[derive(Serialize, ToSchema)]
pub struct PreSignedUrl {
    pub url: String,
    pub fields: std::collections::HashMap<String, String>,
}