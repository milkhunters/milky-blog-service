use std::io::IsTerminal;
use std::sync::Arc;
use actix_web::{web, App, HttpServer};
use actix_web::middleware::Logger;
use std::net::TcpListener;
use std::num::NonZero;
use std::thread;
use tracing::{error, info};
use tracing_subscriber::{fmt, EnvFilter, Layer};
use tracing_subscriber::layer::SubscriberExt;
use tracing_subscriber::util::SubscriberInitExt;
use crate::adapters::database::{postgres, minio};
use crate::adapters::database::minio::file_storage_gateway::MinioFileStorageGateway;
use crate::adapters::database::postgres::article_gateway::PostgresArticleGateway;
use crate::adapters::database::postgres::comment_gateway::PostgresCommentGateway;
use crate::adapters::database::postgres::file_map_gateway::PostgresFileMapGateway;
use crate::adapters::database::postgres::tag_gateway::PostgresTagGateway;
use crate::ioc::IoC;
use crate::presentation::interactor_factory::InteractorFactory;

mod adapters;
mod application;
mod domain;
mod presentation;
mod ioc;
mod app_state;
mod config;

const LOG_LEVEL_ENV: &str = "LOG_LEVEL";
const CONSUL_ADDR_ENV: &str = "CONSUL_ADDR";
const CONSUL_ROOT_ENV: &str = "CONSUL_ROOT";

#[actix_web::main]
async fn main() {
    let log_level = std::env::var(LOG_LEVEL_ENV).unwrap_or_else(|_| "".into());
    let consul_addr = std::env::var(CONSUL_ADDR_ENV).unwrap_or_else(
        |err| { eprintln!("{} {}", CONSUL_ADDR_ENV, err); std::process::exit(1) }
    );
    let consul_root = std::env::var(CONSUL_ROOT_ENV).unwrap_or_else(
        |err| { eprintln!("{} {}", CONSUL_ROOT_ENV, err); std::process::exit(1) }
    );

    let console_layer = fmt::layer()
        .with_ansi(std::io::stdout().is_terminal())
        .with_filter(EnvFilter::new(log_level));

    tracing_subscriber::registry()
        .with(console_layer)
        .init();

    let config = config::Config::from_consul(&consul_addr, &consul_root).await.unwrap_or_else(|error| {
        error!("{}", error);
        std::process::exit(1);
    });

    let postgres_pool = postgres::new_pool(
        &config.database.postgresql.host,
        config.database.postgresql.port,
        &config.database.postgresql.database,
        &config.database.postgresql.username,
        &config.database.postgresql.password
    ).await.unwrap_or_else(|error| {
        error!("failed to create Postgres pool: {}", error);
        std::process::exit(1);
    });

    let s3_client = minio::new_client(
        &config.database.s3.host,
        config.database.s3.port,
        &config.database.s3.access_key,
        &config.database.s3.secret_key,
    ).unwrap_or_else(|error| {
        error!("failed to create S3 client: {}", error);
        std::process::exit(1);
    });

    let article_gateway = PostgresArticleGateway::new(postgres_pool.clone());
    let comment_gateway = PostgresCommentGateway::new(postgres_pool.clone());
    let file_map_gateway = PostgresFileMapGateway::new(postgres_pool.clone());
    let tag_gateway = PostgresTagGateway::new(postgres_pool.clone());
    let file_storage_gateway = MinioFileStorageGateway::new(
        s3_client,
        config.database.s3.bucket.clone(),
        config.database.s3.external_base_url.clone()
    );

    let ioc: Arc<dyn InteractorFactory> = Arc::new(IoC::new(
        Box::new(article_gateway),
        Box::new(comment_gateway),
        Box::new(file_map_gateway),
        Box::new(tag_gateway),
        Box::new(file_storage_gateway)
    ));

    let app_state = app_state::AppState {
        guest_permissions: Arc::new(Default::default()), // todo
        jwt_verify_key: config.general.jwt_verify_key,
    };
    
    let app_builder = move || {
        let ioc: Arc<dyn InteractorFactory> = ioc.clone();
        let ioc_data: web::Data<dyn InteractorFactory> = web::Data::from(ioc.clone());
        App::new()
            .service(web::scope("/api")
                .configure(presentation::rest::article::router)
                .configure(presentation::rest::comment::router)
            )
            .app_data(ioc_data)
            .app_data(web::Data::new(app_state.clone()))
            .wrap(Logger::default()) // todo
    };

    let tcp_listener = TcpListener::bind(format!(
        "{}:{}",
        config.general.host,
        config.general.port
    )).unwrap_or_else(|error| {
        error!("failed to bind TCP listener: {}", error);
        std::process::exit(1);
    });
    
    HttpServer::new(app_builder)
        .workers(thread::available_parallelism().unwrap_or(NonZero::new(1).unwrap()).get())
        .listen(tcp_listener).expect( "failed to listen tcp server")
        .run().await.unwrap_or_else(|error| {
            error!("failed to run HTTP server: {}", error);
            std::process::exit(1);
        });
}
