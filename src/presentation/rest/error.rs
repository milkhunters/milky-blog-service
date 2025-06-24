use crate::application::common::error::AppError;
use crate::domain::error::ValidationError;
use actix_web::http::header::ContentType;
use actix_web::{HttpResponse, ResponseError};
use serde::Serialize;
use serde_json::{json, Value};
use std::fmt::{Display, Formatter};
use crate::adapters::jwt_id_provider::TokenError;

#[derive(Debug, Serialize)]
pub struct HttpErrorDetail {
    field: String,
    reason: String,
    attrs: Vec<Value>,
}


#[derive(Debug)]
pub struct HttpError {
    http_status: actix_web::http::StatusCode,
    app_status: String,
    details: Vec<HttpErrorDetail>
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
            .body(json!({
                "status": self.app_status,
                "details": self.details.iter()
                                .map(|v| serde_json::to_string(v).unwrap())
                                .collect::<Vec<_>>()
            }).to_string())
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
                    field: "APP".into(),
                    reason: msg,
                    attrs: vec![]
                }]
            ),
        };
        HttpError { http_status, app_status, details }
    }
}

impl From<TokenError> for HttpError {
    fn from(err: TokenError) -> Self {
        let (http_status, app_status, details) = match err {
            TokenError::Invalid(msg) => (
                actix_web::http::StatusCode::UNAUTHORIZED,
                "TOKEN_INVALID".into(),
                vec![]
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
                    field: "JWT".into(),
                    reason: msg,
                    attrs: vec![]
                }]
            ),
        };
        HttpError { http_status, app_status, details }
    }
}
