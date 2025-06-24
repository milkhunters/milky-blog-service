use std::sync::Arc;
use tokio::sync::RwLock;
use crate::domain::models::permissions::Permission;

mod adapters;
mod application;
mod domain;
mod presentation;
mod ioc;

pub struct AppConfig {
    pub guest_permissions: Arc<RwLock<Vec<Permission>>>,
    pub jwt_verify_key: [u8; 32]
}

#[actix_web::main]
async fn main() {
    println!("Hello, world!");
}
