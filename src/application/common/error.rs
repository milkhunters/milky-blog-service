use std::collections::HashMap;

use serde::Serialize;
use crate::domain::error::{DomainError, ValidationError};
use super::{
    article_gateway::ArticleGatewayError,
    comment_gateway::CommentGatewayError,
    tag_gateway::TagGatewayError,
    file_map_gateway::FileMapGatewayError,
    file_storage_gateway::FileStorageError,
};


#[derive(Debug, Serialize, Clone)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
    pub enum AppError {
    Validation(HashMap<String, ValidationError>), // status, fields -> reasons ValidationError::*
    NotFound(String), // status, field -> reason NOT_FOUND
    AccessDenied, // status
    Critical(String),
}

impl From<DomainError> for AppError {
    fn from(error: DomainError) -> Self {
        match error {
            DomainError::Validation(err) => AppError::Validation(
                HashMap::from([(err.0, err.1)])
            ),
            DomainError::Access => AppError::AccessDenied,
        }
    }
}

impl From<ArticleGatewayError>  for AppError {
    fn from(error: ArticleGatewayError) -> Self {
        match error {
            ArticleGatewayError::Critical(err) => AppError::Critical(
                format!("critical error in ArticleGateway: {}", err)
            )
        }
    }
}

impl From<CommentGatewayError> for AppError {
    fn from(error: CommentGatewayError) -> Self {
        match error {
            CommentGatewayError::Critical(err) => AppError::Critical(
                format!("critical error in CommentGateway: {}", err)
            )
        }
    }
}

impl From<TagGatewayError> for AppError {
    fn from(error: TagGatewayError) -> Self {
        match error {
            TagGatewayError::Critical(err) => AppError::Critical(
                format!("critical error in TagGateway: {}", err)
            )
        }
    }
}

impl From<FileMapGatewayError> for AppError {
    fn from(error: FileMapGatewayError) -> Self {
        match error {
            FileMapGatewayError::Critical(err) => AppError::Critical(
                format!("critical error in FileMapGateway: {}", err)
            )
        }
    }
}

impl From<FileStorageError> for AppError {
    fn from(error: FileStorageError) -> Self {
        match error {
            FileStorageError::Critical(err) => AppError::Critical(
                format!("critical error in FileStorage: {}", err)
            )
        }
    }
}
