
#[derive(Debug, Clone)]
pub enum DomainError {
    // #[error("you must be authenticated to perform this action")]
    // NotAuth,
    Access,
    Validation(String)
}
