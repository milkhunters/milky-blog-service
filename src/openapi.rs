use utoipa::OpenApi;
use utoipauto::utoipauto;

mod adapters;
mod application;
mod domain;
mod presentation;
mod app_state;


#[utoipauto(paths = "./src")]
#[derive(OpenApi)]
#[openapi(
    info(description = "Milky blog API Documentation", version = "1.0.0"),
)]
struct ApiDoc;

fn main() {
    let openapi = ApiDoc::openapi().to_pretty_json().unwrap();

    std::fs::write("docs/openapi.json", openapi)
        .expect("failed to write OpenAPI schema to file");

    println!("OpenAPI schema generated and saved to docs/openapi.json");
}