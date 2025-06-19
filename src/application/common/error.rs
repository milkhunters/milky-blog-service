use std::collections::HashMap;

use serde::Serialize;
use crate::domain::error::DomainError;
use super::{
    article_gateway::ArticleGatewayError,
    comment_gateway::CommentGatewayError,
    tag_gateway::TagGatewayError,
    file_map_gateway::FileMapGatewayError,
    file_storage_gateway::FileStorageError,
};

#[derive(Debug, Serialize, Clone)]
pub enum ErrorContent {
    Message(String),
    Map(HashMap<String, String>),
}

#[derive(Debug, Serialize, Clone)]
pub enum AppError {
    Validation(ErrorContent),
    NotFound(ErrorContent),
    Conflict(ErrorContent),
    AccessDenied(ErrorContent),
    Critical(ErrorContent),
}

impl From<DomainError> for AppError {
    fn from(error: DomainError) -> Self {
        match error {
            DomainError::Validation(err) => AppError::Validation(ErrorContent::Message(err)),
            DomainError::Access => AppError::AccessDenied(ErrorContent::Message("access denied".into())),
        }
    }
}

impl From<ArticleGatewayError>  for AppError {
    fn from(error: ArticleGatewayError) -> Self {
        match error {
            ArticleGatewayError::Critical(err) => AppError::Critical(ErrorContent::Message(
                format!("critical error in ArticleGateway: {}", err)
            ))
        }
    }
}

impl From<CommentGatewayError> for AppError {
    fn from(error: CommentGatewayError) -> Self {
        match error {
            CommentGatewayError::Critical(err) => AppError::Critical(ErrorContent::Message(
                format!("critical error in CommentGateway: {}", err)
            ))
        }
    }
}

impl From<TagGatewayError> for AppError {
    fn from(error: TagGatewayError) -> Self {
        match error {
            TagGatewayError::Critical(err) => AppError::Critical(ErrorContent::Message(
                format!("critical error in TagGateway: {}", err)
            ))
        }
    }
}

impl From<FileMapGatewayError> for AppError {
    fn from(error: FileMapGatewayError) -> Self {
        match error {
            FileMapGatewayError::Critical(err) => AppError::Critical(ErrorContent::Message(
                format!("critical error in FileMapGateway: {}", err)
            ))
        }
    }
}

impl From<FileStorageError> for AppError {
    fn from(error: FileStorageError) -> Self {
        match error {
            FileStorageError::Critical(err) => AppError::Critical(ErrorContent::Message(
                format!("critical error in FileStorage: {}", err)
            ))
        }
    }
}
