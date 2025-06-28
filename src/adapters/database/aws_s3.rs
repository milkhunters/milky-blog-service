use std::error::Error;
use aws_sdk_s3::{Client};
use aws_sdk_s3::config::{AppName, Credentials, Region, SharedCredentialsProvider, endpoint::ResolveEndpoint};

pub mod file_storage_gateway;


pub fn new_client(
    endpoint: &str,
    access_key: &str,
    secret_key: &str,
    region: &str,
) -> Result<Client, Box<dyn Error>> {
    let config = aws_sdk_s3::Config::builder()
        .region(Region::new(region.to_string()))
        .endpoint_url(endpoint)
        .force_path_style(true)
        .app_name(AppName::new(env!("CARGO_PKG_NAME")).map_err(|_| "Invalid app name")?)
        .credentials_provider(SharedCredentialsProvider::new(Credentials::new(
            access_key,
            secret_key,
            None,
            None,
            "s3_credentials"
        ))).build();
    
    Ok(Client::from_conf(config))
}
