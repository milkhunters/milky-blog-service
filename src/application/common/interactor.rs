use super::error::AppError;

pub trait Interactor<I, O> {
    async fn execute(&self, input: I) -> Result<O, AppError>;
}