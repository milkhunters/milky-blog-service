use crate::application::common::error::{AppError, TokenError};
use crate::domain::error::ValidationError;
use actix_web::http::header::ContentType;
use actix_web::{HttpResponse, ResponseError};
use serde::Serialize;
use serde_json::Value;
use std::fmt::{Display, Formatter};
use utoipa::ToSchema;

#[derive(Debug, Serialize, ToSchema)]
pub struct HttpErrorDetail {
    #[schema(example = "id")]
    field: String,
    #[schema(example = "NOT_FOUND")]
    reason: String,
    attrs: Vec<Value>,
}

#[derive(Debug, Serialize, ToSchema)]
pub struct HttpErrorModel {
    #[schema(example = "NOT_FOUND")]
    status: String,
    details: Vec<HttpErrorDetail>,
}


#[derive(Debug)]
pub struct HttpError {
    http_status: actix_web::http::StatusCode,
    inner: HttpErrorModel
}

impl Display for HttpError {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "{:?}", self)
    }
}

impl ResponseError for  HttpError {
    fn status_code(&self) -> actix_web::http::StatusCode {
        self.http_status
    }

    fn error_response(&self) -> HttpResponse {
        HttpResponse::build(self.status_code())
            .insert_header(ContentType::json())
            .status(self.status_code())
            .body(serde_json::to_string(&self.inner).unwrap())
    }
}

impl From<AppError> for HttpError {
    fn from(err: AppError) -> Self {
        let (http_status, app_status, details) = match err {
            AppError::NotFound(field) => (
                actix_web::http::StatusCode::NOT_FOUND,
                "NOT_FOUND".into(),
                vec![HttpErrorDetail {
                    field,
                    reason: "NOT_FOUND".into(),
                    attrs: vec![],
                }]
            ),
            AppError::AccessDenied => (
                actix_web::http::StatusCode::FORBIDDEN,
                "ACCESS_DENIED".into(),
                vec![]
            ),
            AppError::Validation(fields) => (
                actix_web::http::StatusCode::BAD_REQUEST,
                "VALIDATION".into(),
                fields.into_iter().map(|(field, reason)| {
                    let (attrs, reason) = match reason {
                        ValidationError::InvalidEmpty => (
                            vec![],
                            "INVALID_EMPTY".into(),
                        ),
                        ValidationError::InvalidRange(min, max) => (
                            vec![Value::Number(min.into()), Value::Number(max.into())],
                            "INVALID_RANGE".into(),
                        ),
                        ValidationError::InvalidRegex(re_str) => (
                            vec![Value::String(re_str)],
                            "INVALID_REGEX".to_string(),
                        )
                    };
                    HttpErrorDetail { field, reason, attrs }
                }).collect()
            ),
            AppError::Critical(msg) => (
                actix_web::http::StatusCode::INTERNAL_SERVER_ERROR,
                "CRITICAL".into(),
                vec![HttpErrorDetail {
                    field: "app".into(),
                    reason: "CRITICAL".into(),
                    attrs: vec![Value::String(msg)]
                }]
            ),
        };
        HttpError { http_status, inner: HttpErrorModel { status: app_status, details } }
    }
}

impl From<TokenError> for HttpError {
    fn from(err: TokenError) -> Self {
        let (http_status, app_status, details) = match err {
            TokenError::Invalid(msg) => (
                actix_web::http::StatusCode::UNAUTHORIZED,
                "TOKEN_INVALID".into(),
                vec![HttpErrorDetail {
                    field: "jwt".into(),
                    reason: "TOKEN_INVALID".into(),
                    attrs: vec![Value::String(msg)]
                }]
            ),
            TokenError::Expired => (
                actix_web::http::StatusCode::UNAUTHORIZED,
                "TOKEN_EXPIRED".into(),
                vec![]
            ),
            TokenError::Critical(msg) => (
                actix_web::http::StatusCode::INTERNAL_SERVER_ERROR,
                "CRITICAL".into(),
                vec![HttpErrorDetail {
                    field: "CRITICAL".into(),
                    reason: msg,
                    attrs: vec![]
                }]
            ),
        };
        HttpError { http_status, inner: HttpErrorModel { status: app_status, details } }
    }
}

impl HttpErrorModel {
    pub fn not_found(field: String) -> Self {
        HttpErrorModel {
            status: "NOT_FOUND".into(),
            details: vec![HttpErrorDetail {
                field,
                reason: "NOT_FOUND".into(),
                attrs: vec![],
            }],
        }
    }
    
    pub fn access_denied() -> Self {
        HttpErrorModel {
            status: "ACCESS_DENIED".into(),
            details: vec![],
        }
    }
    
    pub fn token_invalid(msg: String) -> Self {
        HttpErrorModel {
            status: "TOKEN_INVALID".into(),
            details: vec![HttpErrorDetail {
                field: "jwt".into(),
                reason: "TOKEN_INVALID".into(),
                attrs: vec![Value::String(msg)],
            }],
        }
    }
    
    pub fn token_expired() -> Self {
        HttpErrorModel {
            status: "TOKEN_EXPIRED".into(),
            details: vec![],
        }
    }
    
    pub fn validation(fields: Vec<(String, ValidationError)>) -> Self {
        HttpErrorModel {
            status: "VALIDATION".into(),
            details: fields.into_iter().map(|(field, reason)| {
                let (attrs, reason) = match reason {
                    ValidationError::InvalidEmpty => (vec![], "INVALID_EMPTY".into()),
                    ValidationError::InvalidRange(min, max) => (
                        vec![Value::Number(min.into()), Value::Number(max.into())],
                        "INVALID_RANGE".into(),
                    ),
                    ValidationError::InvalidRegex(re_str) => (
                        vec![Value::String(re_str)],
                        "INVALID_REGEX".to_string(),
                    ),
                };
                HttpErrorDetail { field, reason, attrs }
            }).collect(),
        }
    }
    
    pub fn critical(msg: String) -> Self {
        HttpErrorModel {
            status: "CRITICAL".into(),
            details: vec![HttpErrorDetail {
                field: "app".into(),
                reason: "CRITICAL".into(),
                attrs: vec![Value::String(msg)],
            }],
        }
    }
}