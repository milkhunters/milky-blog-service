use crate::adapters::jwt_id_provider::{JwtIdProvider, TokenError};
use crate::application::common::id_provider::IdProvider;
use crate::AppConfig;
use actix_web::HttpRequest;
use std::fmt::Display;

const COOKIE_JWT: &str = "auth_token";

pub async fn new_jwt_id_provider(req: &HttpRequest, app_config: &AppConfig) -> Result<Box<dyn IdProvider>, TokenError> {
    let token: String = req.cookie(COOKIE_JWT)
        .and_then(|cookie| cookie.value().parse().ok())
        .unwrap_or_default();

    Ok(Box::new(JwtIdProvider::new(
        &token,
        app_config.guest_permissions.read().await.clone(), // todo from cache
        &app_config.jwt_verify_key
    )?))
}
