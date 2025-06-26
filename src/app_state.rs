use std::sync::Arc;
use tokio::sync::RwLock;
use crate::domain::models::permissions::Permission;

#[derive(Clone)]
pub struct AppState {
    pub guest_permissions: Arc<RwLock<Vec<Permission>>>,
    pub jwt_verify_key: [u8; 32]
}
