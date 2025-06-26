pub mod file_storage_gateway;

use minio::s3::creds::StaticProvider;
use minio::s3::error::Error;
use minio::s3::Client;

pub fn new_client(
    host: &str,
    port: u16,
    access_key: &str,
    secret_key: &str
) -> Result<Client, Error> {
    let endpoint = format!("{}:{}", host, port);

    let static_provider = StaticProvider::new(access_key, secret_key, None);
    Client::new(
        endpoint.parse()?,
        Some(Box::new(static_provider)),
        None,
        Some(true)
    )
}
