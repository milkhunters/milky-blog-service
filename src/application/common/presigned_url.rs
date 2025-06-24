use serde::Serialize;

#[derive(Serialize)]
pub struct PreSignedUrl {
    pub url: String,
    pub fields: std::collections::HashMap<String, String>,
}