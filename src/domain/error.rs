use thiserror::Error;

#[derive(Error, Debug, Clone)]
pub enum DomainError {
    #[error("access denied")]
    Access,
    #[error("validation: {0}")]
    Validation(String)
}
