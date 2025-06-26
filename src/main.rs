use std::sync::Arc;
use tokio::sync::RwLock;
use crate::domain::models::permissions::Permission;

mod adapters;
mod application;
mod domain;
mod presentation;
mod ioc;
mod app_state;

#[actix_web::main]
async fn main() {
    println!("Hello, world!");
}
