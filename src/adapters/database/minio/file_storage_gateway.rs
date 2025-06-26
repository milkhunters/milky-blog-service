use async_trait::async_trait;
use chrono::{DateTime, Utc};
use minio::s3::builders::PostPolicy;
use minio::s3::types::S3Api;
use minio::s3::utils::utc_now;
use crate::application::common::file_storage_gateway::{FileStorageError, FileStorageReader, FileStorageLinker, FileStorageRemover, FileStorageGateway};
use crate::application::common::presigned_url::PreSignedUrl;
use crate::domain::models::article::ArticleId;
use crate::domain::models::file::FileId;

pub struct MinioFileStorageGateway {
    client: minio::s3::Client,
    bucket_name: String,
    external_link: String
}

impl MinioFileStorageGateway {
    pub fn new(client: minio::s3::Client, bucket_name: String, external_link: String) -> Self {
        MinioFileStorageGateway { client, bucket_name, external_link }
    }
}

#[async_trait]
impl FileStorageReader for MinioFileStorageGateway {
    async fn is_exist_file(&self, article_id: &ArticleId, id: &FileId) -> Result<bool, FileStorageError> {
        let object_name = format!("{}/{}", article_id, id);
        match self.client.stat_object(&self.bucket_name, &object_name).send().await {
            Ok(_) => Ok(true),
            // Err(minio::s3::error::Error::NoSuchKey(_)) => Ok(false), // todo fix it
            Err(e) => Err(FileStorageError::Critical(e.to_string())),
        }
    }
}

#[async_trait]
impl FileStorageLinker for MinioFileStorageGateway {
    async fn upload_link(
        &self, 
        article_id: &ArticleId, 
        file_id: &FileId, 
        content_type: &str, 
        content_length: (u64, u64), 
        ttl: chrono::Duration
    ) -> Result<PreSignedUrl, FileStorageError> {
        let expiration: DateTime<Utc> = utc_now() + ttl;
        let mut policy = PostPolicy::new(&self.bucket_name, expiration).unwrap();
        policy.add_equals_condition("key", &file_id.to_string()).unwrap();
        policy.add_equals_condition("Content-Type", content_type).unwrap();
        policy.add_content_length_range_condition(content_length.0 as usize, content_length.1 as usize).unwrap();
        
        let presigned_url = self.client
            .get_presigned_post_form_data(policy)
            .send().await;
        
        let fields = match presigned_url {
            Ok(url) => url,
            Err(e) => return Err(FileStorageError::Critical(e.to_string())), // todo if not found then normal error
        };
        
        let url = format!("{}/{}/{}", self.external_link, self.bucket_name, article_id);

        Ok(PreSignedUrl {
            url,
            fields,
        })
    }

    fn download_link(&self, article_id: &ArticleId, file_id: &FileId) -> String {
        format!("{}/{}/{}/{}", self.external_link, self.bucket_name,  article_id, file_id)
    }
}


#[async_trait]
impl FileStorageRemover for MinioFileStorageGateway {
    async fn remove(&self, article_id: &ArticleId, file_id: &FileId) -> Result<(), FileStorageError> {
        let object_name = format!("{}/{}", article_id, file_id);
        match self.client.delete_object(&self.bucket_name, &object_name).send().await {
            Ok(_) => Ok(()),
            Err(e) => Err(FileStorageError::Critical(e.to_string())),
        }
    }
}


#[async_trait]
impl FileStorageGateway for MinioFileStorageGateway {}
