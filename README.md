![TeamCity build status](https://teamcity.milkhunters.ru/app/rest/builds/buildType:id:MilkhuntersBackend_Build_Prod/statusIcon.svg)

# Milky blog

## Env
| Variable    | Description                                               |
|-------------|-----------------------------------------------------------|
| LOG_LEVEL   | Log level for the service (default: none)                 |
| CONSUL_ADDR | Address of the Consul server (ex: http://localhost:8500)  |
| CONSUL_ROOT | Root path in Consul for service config (ex: `milky-blog`) |

## Consul config

Example:
```yaml
general:
    host: 0.0.0.0
    port: 8080
    jwt_verify_key: MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEPnvzPHFBcMFK81z16B8G6Ckn6BUcozMXu/DdLy9o3JeKb7Q8Fl2ITGVfeG61JX3zkO4kE0UpMy4Q+dy7kN2jcw==
database:
    postgresql:
        host: postgres
        port: 5432
        username: blog
        password: blog
        database: blog
    s3:
        host: minio
        port: 9000
        access_key: blog-user
        secret_key: blog-secret
        bucket: article-assets
        external_base_url: http://localhost:9000
```

## Run

### Manually
```bash
export LOG_LEVEL=info
export CONSUL_ADDR=http://localhost:8500
export CONSUL_ROOT=milky-blog

cargo run --release --bin milky-blog-service
```

### Docker

```bash
docker compose up -d --build
```

## Test

```bash
cargo test --release
```