use crate::application::common::file_storage_gateway::{FileStorageError, FileStorageGateway, FileStorageLinker, FileStorageReader, FileStorageRemover};
use crate::application::common::presigned_url::UploadUrl;
use crate::domain::models::article::ArticleId;
use crate::domain::models::file::FileId;
use async_trait::async_trait;
use aws_sdk_s3::config::Credentials;
use aws_sdk_s3::error::SdkError;
use aws_sdk_s3::operation::head_object::HeadObjectError;
use aws_sdk_s3::Client;
use aws_sigv4::http_request::{sign, PayloadChecksumKind, SignableBody, SignableRequest, SignatureLocation, SigningSettings};
use aws_sigv4::sign::v4;
use aws_smithy_runtime_api::client::identity::Identity;
use std::collections::HashMap;
use std::time::SystemTime;
use url::Url;


pub struct AwsS3FileStorageGateway {
    client: Client,
    bucket_name: String,
    external_endpoint: String,
    identity: Identity
}

impl AwsS3FileStorageGateway {
    pub fn new(
        client: Client,
        bucket_name: String,
        access_key: &str,
        secret_key: &str,
        external_endpoint: String
    ) -> Self {
        Self {
            client,
            bucket_name,
            identity: Credentials::new(
                access_key,
                secret_key,
                None,
                None,
                "s3_credentials"
            ).into(),
            external_endpoint: external_endpoint.trim_end_matches("/").into()
        }
    }
}

#[async_trait]
impl FileStorageReader for AwsS3FileStorageGateway {
    async fn is_exist_file(&self, article_id: &ArticleId, id: &FileId) -> Result<bool, FileStorageError> {
        let object_key = format!("{}/{}", article_id, id);
        match self.client.head_object()
            .bucket(&self.bucket_name)
            .key(object_key)
            .send()
            .await
        {
            Ok(_) => Ok(true),
            Err(SdkError::ServiceError(e)) => match e.into_err() {
                HeadObjectError::NotFound(_) => Ok(false),
                err => Err(FileStorageError::Critical(err.to_string())),
            },
            Err(e) => Err(FileStorageError::Critical(
                format!("sdk error: {}", e.to_string())
            ))
        }
    }
}

#[async_trait]
impl FileStorageLinker for AwsS3FileStorageGateway {
    async fn upload_link(
        &self, 
        article_id: &ArticleId, 
        file_id: &FileId, 
        content_type: &str, 
        content_length: (u64, u64), 
        ttl: chrono::Duration
    ) -> Result<UploadUrl, FileStorageError> {
        let object_key = format!("{}/{}", article_id, file_id);

        // Sign by AWS SDK S3 PresigningConfig
        // let presigned_request = self.client.put_object()
        //     .bucket(&self.bucket_name)
        //     .key(object_key)
        //     .content_type(content_type)
        //     .presigned(PresigningConfig::expires_in(ttl.to_std().unwrap()).map_err(
        //         |e| FileStorageError::Critical(format!(
        //             "presigned config: {}", e.to_string()
        //         )))?
        //     )
        //     .await
        //     .map_err(|e| FileStorageError::Critical(format!(
        //         "presigned request: {}", e.to_string()
        //     )))?;
        // 
        // let url = presigned_request.uri().replacen(
        //     &self.internal_endpoint,
        //     &self.external_endpoint,
        //     1
        // );
        
        
        // Manually sign the request using aws-sigv4
        let url = format!("{}/{}/{}", self.external_endpoint, self.bucket_name, object_key);
        let mut url = Url::parse(&url).map_err(|e| FileStorageError::Critical(format!(
            "parse URL: {}", e
        )))?;
        
        url.query_pairs_mut().append_pair("X-id", "PutObject");
        
        
        let mut settings = SigningSettings::default();
        settings.expires_in = Some(ttl.to_std().unwrap());
        settings.payload_checksum_kind = PayloadChecksumKind::XAmzSha256;
        settings.signature_location = SignatureLocation::QueryParams;
        
        let region = self.client.config().region()
            .map(|r| r.to_string())
            .unwrap_or_else(|| "us-east-1".into());
        
        let params = v4::SigningParams::builder()
            .identity(&self.identity)
            .region(&region)
            .name("s3")
            .time(SystemTime::now())
            .settings(settings)
            .build()
            .map_err(|e| FileStorageError::Critical(format!("build signing params: {}", e)))?;
        
        let headers = [
            ("host", self.external_endpoint.trim_start_matches("http://").trim_end_matches("/")),
            ("content-type", content_type)
        ].into_iter();
        
        let request = SignableRequest::new(
            "PUT",
            url.as_str(),
            headers.clone(),
            SignableBody::UnsignedPayload
        ).map_err(|e| FileStorageError::Critical(format!("create signable request: {}", e)))?;
        
        let (instructions, signature) = sign(request, &params.into())
            .map_err(|e| FileStorageError::Critical(format!("sign request: {}", e)))?
            .into_parts();
        
        for (name, value) in instructions.params() {
            url.query_pairs_mut().append_pair(name, value);
        }

        Ok(UploadUrl {
            url: url.to_string(),
            method: "PUT".into(),
            headers: headers.map(|(k, v)| {
                (k.to_string(), v.to_string())
            }).collect::<HashMap<_, _>>(),
            // headers: instructions.headers().map(|(k, v)| {
            //     (k.to_string(), v.to_string())
            // }).collect::<HashMap<_, _>>()
        })
    }

    fn download_link(&self, article_id: &ArticleId, file_id: &FileId) -> String {
        format!("{}/{}/{}/{}", self.external_endpoint, self.bucket_name,  article_id, file_id)
    }
}


#[async_trait]
impl FileStorageRemover for AwsS3FileStorageGateway {
    async fn remove(&self, article_id: &ArticleId, file_id: &FileId) -> Result<(), FileStorageError> {
        let object_name = format!("{}/{}", article_id, file_id);
        match self.client.delete_object()
            .bucket(&self.bucket_name)
            .key(object_name)
            .send()
            .await
        {
            Ok(_) => Ok(()),
            Err(e) => Err(FileStorageError::Critical(
                format!("delete object: {}", e.to_string())
            )),
        }
    }
}


#[async_trait]
impl FileStorageGateway for AwsS3FileStorageGateway {}
