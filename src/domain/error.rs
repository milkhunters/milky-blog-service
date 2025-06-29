use serde::Serialize;

#[derive(Debug, Serialize, Clone)]
pub enum ValidationError {
    InvalidRange(i64, i64),
    InvalidEmpty,
    InvalidRegex(String),
}


pub enum DomainError {
    Access,
    Validation((String, ValidationError))
}
