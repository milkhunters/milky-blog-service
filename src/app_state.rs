use std::sync::Arc;
use tokio::sync::RwLock;
use crate::domain::models::permissions::Permission;

pub struct AppConfig {
    pub guest_permissions: Arc<RwLock<Vec<Permission>>>,
    pub jwt_verify_key: [u8; 32]
}
