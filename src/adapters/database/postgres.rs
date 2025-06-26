pub mod article_gateway;
pub mod comment_gateway;
pub mod file_map_gateway;
pub mod tag_gateway;

use sqlx::postgres::PgPoolOptions;

pub async fn new_pool(
    host: &str,
    port: u16,
    database: &str,
    username: &str,
    password: &str
) -> Result<sqlx::PgPool, sqlx::Error> {
    let options = sqlx::postgres::PgConnectOptions::new()
        .host(host)
        .port(port)
        .database(database)
        .username(username)
        .password(password)
        .application_name(env!("CARGO_PKG_NAME"))
        .ssl_mode(sqlx::postgres::PgSslMode::Disable);

    let pool = PgPoolOptions::new()
        .max_connections(20)
        .min_connections(5)
        .connect_with(options)
        .await?;

    sqlx::migrate!("./migrations").run(&pool).await?;
    
    Ok(pool)
}