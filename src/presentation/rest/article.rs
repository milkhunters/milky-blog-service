use crate::application::{
    article::{
        delete::DeleteArticleInput,
        file::{
            confirm::ConfirmArticleFileInput,
            create::CreateArticleFileInput,
            delete::DeleteArticleFileInput,
        },
        get::GetArticleInput,
        rate::RateArticleInput,
        tag::find::FindArticleTagsInput,
        update::UpdateArticleInput,
        find::FindArticleInput,
        create::CreateArticleInput
    },
    common::interactor::Interactor
};
use crate::domain::models::{
    article::ArticleId,
    article_state::ArticleState,
    file::FileId
};
use crate::presentation::{
    interactor_factory::InteractorFactory,
    rest::error::HttpError,
    rest::id_provider::new_jwt_id_provider
};
use crate::AppConfig;
use actix_web::{delete, get, post, put, web, HttpRequest, HttpResponse};
use serde::Deserialize;

pub fn router(cfg: &mut web::ServiceConfig) {
    cfg.service(
        web::scope("/articles")
            .service(create_article)
            .service(get_article)
            .service(find_article)
            .service(update_article)
            .service(delete_article)
            .service(rate_article)
            .service(
                web::scope("/files")
                    .service(confirm_article_file)
                    .service(create_article_file)
                    .service(delete_article_file)
            )
            .service(
                web::scope("/tags")
                    .service(find_article_tags)
            )
    );
}


#[post("")]
async fn create_article(
    input: web::Json<CreateArticleInput>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppConfig>,
    req: HttpRequest
) -> Result<HttpResponse, HttpError> {
    let id_provider = new_jwt_id_provider(&req, &app_config).await?;
    let output = ioc.create_article(id_provider).execute(input.into_inner()).await?;
    Ok(HttpResponse::Ok().json(output))
}

#[delete("/{id}")]
async fn delete_article(
    input: web::Path<ArticleId>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppConfig>,
    req: HttpRequest
) -> Result<HttpResponse, HttpError> {
    let id_provider = new_jwt_id_provider(&req, &app_config).await?;
    let output = ioc.delete_article(id_provider).execute(
        DeleteArticleInput { id: input.into_inner() }
    ).await?;
    Ok(HttpResponse::Ok().json(output))
}

#[get("{id}")]
async fn get_article(
    input: web::Path<ArticleId>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppConfig>,
    req: HttpRequest
) -> Result<HttpResponse, HttpError> {
    let id_provider = new_jwt_id_provider(&req, &app_config).await?;
    let output = ioc.get_article(id_provider).execute(
        GetArticleInput{ id: input.into_inner()}
    ).await?;
    Ok(HttpResponse::Ok().json(output))
}

#[get("")]
async fn find_article(
    input: web::Query<FindArticleInput>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppConfig>,
    req: HttpRequest
) -> Result<HttpResponse, HttpError> {
    let id_provider = new_jwt_id_provider(&req, &app_config).await?;
    let output = ioc.find_article(id_provider).execute(input.into_inner()).await?;
    Ok(HttpResponse::Ok().json(output))
}

#[post("rate/{id}")]
async fn rate_article(
    input: web::Path<ArticleId>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppConfig>,
    req: HttpRequest
) -> Result<HttpResponse, HttpError> {
    let id_provider = new_jwt_id_provider(&req, &app_config).await?;
    let output = ioc.rate_article(id_provider).execute(
        RateArticleInput { id: input.into_inner() }
    ).await?;
    Ok(HttpResponse::Ok().json(output))
}


#[derive(Deserialize)]
pub struct UpdateArticleJson {
    pub title: String,
    pub content: String,
    pub state: ArticleState,
    pub poster: Option<FileId>,
    pub tags: Vec<String>
}

#[put("{id}")]
async fn update_article(
    id: web::Path<ArticleId>,
    body: web::Json<UpdateArticleJson>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppConfig>,
    req: HttpRequest
) -> Result<HttpResponse, HttpError> {
    let body = body.into_inner();
    let input = UpdateArticleInput {
        id: id.into_inner(),
        title: body.title.clone(),
        content: body.content.clone(),
        state: body.state,
        poster: body.poster,
        tags: body.tags.clone()
    };
    let id_provider = new_jwt_id_provider(&req, &app_config).await?;
    let output = ioc.update_article(id_provider).execute(input).await?;
    Ok(HttpResponse::Ok().json(output))
}

#[post("{id}/confirm")]
async fn confirm_article_file(
    id: web::Json<FileId>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppConfig>,
    req: HttpRequest
) -> Result<HttpResponse, HttpError> {
    let id_provider = new_jwt_id_provider(&req, &app_config).await?;
    let output = ioc.confirm_article_file(id_provider).execute(
        ConfirmArticleFileInput { id: id.into_inner() }
    ).await?;
    Ok(HttpResponse::Ok().json(output))
}

#[post("")]
async fn create_article_file(
    input: web::Json<CreateArticleFileInput>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppConfig>,
    req: HttpRequest
) -> Result<HttpResponse, HttpError> {
    let id_provider = new_jwt_id_provider(&req, &app_config).await?;
    let output = ioc.create_article_file(id_provider).execute(input.into_inner()).await?;
    Ok(HttpResponse::Ok().json(output))
}

#[delete("{id}")]
async fn delete_article_file(
    id: web::Path<FileId>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppConfig>,
    req: HttpRequest
) -> Result<HttpResponse, HttpError> {
    let id_provider = new_jwt_id_provider(&req, &app_config).await?;
    let output = ioc.delete_article_file(id_provider).execute(
        DeleteArticleFileInput { id: id.into_inner() }
    ).await?;
    Ok(HttpResponse::Ok().json(output))
}

#[get("")]
async fn find_article_tags(
    input: web::Query<FindArticleTagsInput>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppConfig>,
    req: HttpRequest
) -> Result<HttpResponse, HttpError> {
    let id_provider = new_jwt_id_provider(&req, &app_config).await?;
    let output = ioc.find_article_tags(id_provider).execute(input.into_inner()).await?;
    Ok(HttpResponse::Ok().json(output))
}
