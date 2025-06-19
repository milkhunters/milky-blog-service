use std::collections::HashMap;

use serde::Serialize;
use crate::domain::error::DomainError;

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
    AccessDenied(ErrorContent)
}

impl From<DomainError> for AppError {
    fn from(error: DomainError) -> Self {
        match error {
            DomainError::Validation(err) => AppError::Validation(ErrorContent::Message(err)),
            DomainError::Access => AppError::AccessDenied(ErrorContent::Message("access denied".into())),
        }
    }
}