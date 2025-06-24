use jsonwebtoken::{decode, Algorithm, DecodingKey, Validation};
use crate::application::common::id_provider::IdProvider;
use crate::domain::models::{
    permissions::Permission,
    user_id::UserId,
    user_state::UserState
};
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
struct JwtPayload {
    user_id: UserId,
    permissions: Vec<Permission>,
    user_state: UserState,
    exp: usize,
}

#[derive(Debug)]
pub enum TokenError {
    Invalid(String),
    Expired,
    Critical(String),
}

pub struct JwtIdProvider {
    user_id: UserId,
    permissions: Vec<Permission>,
    user_state: UserState,
}

impl JwtIdProvider {
    pub fn new(
        token: &String,
        guest_perms: Vec<Permission>,
        verify_key: &[u8],
    ) -> Result<Self, TokenError> {
        if token.is_empty() {
            return Ok(Self {
                user_id: UserId::default(),
                permissions: guest_perms,
                user_state: UserState::Active,
            });
        }
        
        let mut validation = Validation::new(Algorithm::ES256);
        validation.validate_exp = true;

        let token_data = match decode::<JwtPayload>(
            token,
            &DecodingKey::from_ec_pem(verify_key)
                .map_err(|e| TokenError::Critical(format!("invalid jwt verify key: {}", e)))?,
            &validation
        ) {
            Ok(data) => data,
            Err(e) => return match e.kind() {
                jsonwebtoken::errors::ErrorKind::ExpiredSignature => {
                    Err(TokenError::Expired)
                }
                _ => Err(TokenError::Invalid(format!("token verification failed: {}", e))),
            },
        };

        Ok(Self {
            user_id: token_data.claims.user_id,
            permissions: token_data.claims.permissions,
            user_state: token_data.claims.user_state,
        })
    }
}

impl IdProvider for JwtIdProvider {
    fn user_id(&self) -> &UserId {
        &self.user_id
    }

    fn user_state(&self) -> &UserState {
        &self.user_state
    }

    fn permissions(&self) -> &Vec<Permission> {
        &self.permissions
    }
}