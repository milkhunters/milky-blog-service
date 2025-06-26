use consulrs::client::{ConsulClient, ConsulClientSettingsBuilder};
use consulrs::kv;
use serde::Deserialize;

#[derive(Debug, Clone, Deserialize)]
pub struct General {
    pub host: String,
    pub port: u16,
    pub jwt_verify_key: [u8; 32],
}

#[derive(Debug, Clone, Deserialize)]
pub struct Postgresql {
    pub host: String,
    pub port: u16,
    pub username: String,
    pub password: String,
    pub database: String,
}

#[derive(Debug, Clone, Deserialize)]
pub struct S3 {
    pub host: String,
    pub port: u16,
    pub access_key: String,
    pub secret_key: String,
    pub bucket: String,
    pub region: String,
    pub external_base_url: String
}

#[derive(Debug, Clone, Deserialize)]
pub struct Database {
    pub postgresql: Postgresql,
    pub s3: S3,
}

#[derive(Debug, Clone, Deserialize)]
pub struct Config {
    pub general: General,
    pub database: Database,
}


impl Config {
    pub async fn from_consul(address: &str, key: &str) -> Result<Config, String> {
        let client = ConsulClient::new(
            ConsulClientSettingsBuilder::default()
                .address(address)
                .build()
                .expect("ConsulClientSettingsBuilder build failed")
        ).expect("ConsulClient::new failed");

        let mut res = kv::read(&client, &key, None).await.
            map_err(|e| format!("failed to read key from consul: {}", e))?;

        let raw_yaml: String = res.response.pop().unwrap().value.unwrap().try_into()
            .map_err(|e| format!("failed to convert consul value to string: {}", e))?;

        serde_yaml::from_str::<Config>(&*raw_yaml)
            .map_err(|e| format!("failed to deserialize config from yaml: {}", e))
    }
}
