use serde::Serialize;
use utoipa::ToSchema;

#[derive(Serialize, ToSchema)]
pub struct PreSignedUrl {
    #[schema(example = "https://s3.example.com/article-assets/987e9dc9-d84c-4ba7-837f-db755a0fdc55/80bbc0bc-4064-420a-b4ed-4f94b4575321")]
    pub url: String,
    pub fields: std::collections::HashMap<String, String>,
}