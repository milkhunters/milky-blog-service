use std::collections::HashMap;
use serde::Serialize;

#[derive(Serialize)]
pub struct UploadUrl {
    pub url: String,
    pub method: String,
    pub headers: HashMap<String, String>,
}