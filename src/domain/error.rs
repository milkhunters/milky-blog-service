use thiserror::Error;

#[derive(Error, Debug, Clone)]
pub enum DomainError {
    #[error("you must be authenticated to perform this action")]
    NotAuth,
    #[error("access denied")]
    Access,
    #[error("validation: {0}")]
    Validation(String)
}
