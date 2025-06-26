use crate::app_state::AppConfig;
use crate::application::article::create::CreateArticleOutput;
use crate::application::{
    article::{
        create::CreateArticleInput,
        delete::DeleteArticleInput,
        file::{
            confirm::ConfirmArticleFileInput,
            create::CreateArticleFileInput,
            delete::DeleteArticleFileInput,
        },
        find::FindArticleInput,
        get::GetArticleInput,
        rate::RateArticleInput,
        tag::find::FindArticleTagsInput,
        update::UpdateArticleInput as UpdateArticleInputInt
    },
    common::interactor::Interactor
};
use crate::domain::models::rate_state::RateState;
use crate::domain::models::{
    article::ArticleId,
    article_state::ArticleState,
    file::FileId
};
use crate::presentation::rest::error::HttpErrorModel;
use crate::presentation::{
    interactor_factory::InteractorFactory,
    rest::error::HttpError,
    rest::id_provider::new_jwt_id_provider
};
use actix_web::{delete, get, post, put, web, HttpRequest, HttpResponse};
use serde::Deserialize;
use utoipa::ToSchema;

const ARTICLES: &str = "articles";
const ARTICLES_FILES: &str = "articles/files";
const ARTICLES_TAGS: &str = "articles/tags";

pub fn router(cfg: &mut web::ServiceConfig) {
    cfg.service(
        utoipa_actix_web::scope(ARTICLES)
            .service(create_article)
            .service(get_article)
            .service(find_article)
            .service(update_article)
            .service(delete_article)
            .service(rate_article)
            .service(
                utoipa_actix_web::scope("/files")
                    .service(confirm_article_file)
                    .service(create_article_file)
                    .service(delete_article_file)
            )
            .service(
                utoipa_actix_web::scope("/tags")
                    .service(find_article_tags)
            )
    );
}


/// Create new article.
///
/// Post a new `Article` in request body as json to store it. Api will return
/// created `ArticleId`
///
#[utoipa::path(
    tag = ARTICLES,
    responses(
        (status = 201, description = "Created successfully", body = CreateArticleOutput),
        (status = 400, description = "Validation error", body = HttpErrorModel)
    )
)]
#[post("")]
async fn create_article(
    input: web::Json<CreateArticleInput>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppConfig>,
    req: HttpRequest
) -> Result<HttpResponse, HttpError> {
    let id_provider = new_jwt_id_provider(&req, &app_config).await?;
    let output = ioc.create_article(id_provider).execute(input.into_inner()).await?;
    Ok(HttpResponse::Created().json(output))
}

/// Delete article by id.
///
/// Delete an `Article` by its `ArticleId`. Api will return deleted `ArticleId`.
///
#[utoipa::path(
    tag = ARTICLES,
)]
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

/// Get article by id.
///
/// Get an `Article` by its `ArticleId`. Api will return found `Article`.
///
#[utoipa::path(
    tag = ARTICLES, 
)]
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

/// Find articles by criteria.
///
/// Find articles by criteria specified in query parameters. Api will return
/// a list of found `Article` objects.
#[utoipa::path(
    tag = ARTICLES,
)]
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

/// Rate article by id.
///
/// Rate an `Article` by its `ArticleId` and `RateState`. Api will return
/// updated `Article` with new rating state.
///
#[utoipa::path(
    tag = ARTICLES,
)]
#[post("rate/{id}/{state}")]
async fn rate_article(
    input: web::Path<ArticleId>,
    state: web::Path<RateState>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppConfig>,
    req: HttpRequest
) -> Result<HttpResponse, HttpError> {
    let id_provider = new_jwt_id_provider(&req, &app_config).await?;
    let output = ioc.rate_article(id_provider).execute(
        RateArticleInput { id: input.into_inner(), state: state.into_inner() }
    ).await?;
    Ok(HttpResponse::Ok().json(output))
}


/// Update article by id.
///
/// Update an `Article` by its `ArticleId`. Api will return updated `Article`.
///
#[derive(Deserialize, ToSchema)]
pub struct UpdateArticleInput {
    pub title: String,
    pub content: String,
    pub state: ArticleState,
    pub poster: Option<uuid::Uuid>,
    pub tags: Vec<String>
}

/// Update an existing article.
///
/// Update an `Article` by its `ArticleId`. Api will return updated `Article`.
///
#[utoipa::path(
    tag = ARTICLES,
)]
#[put("{id}")]
async fn update_article(
    id: web::Path<ArticleId>,
    body: web::Json<UpdateArticleInput>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppConfig>,
    req: HttpRequest
) -> Result<HttpResponse, HttpError> {
    let body = body.into_inner();
    let input = UpdateArticleInputInt {
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

/// Confirm article file by id.
///
/// Confirm an `ArticleFile` by its `FileId`. Api will return confirmed
/// `ArticleFile`.
#[utoipa::path(
    tag = ARTICLES_FILES,
)]
#[post("{id}/confirm")]
async fn confirm_article_file(
    id: web::Json<uuid::Uuid>,
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


/// Create new article file.
///
/// Post a new `ArticleFile` in request body as json to store it. Api will return
/// created `FileId` of the article file.
///
#[utoipa::path(
    tag = ARTICLES_FILES
)]
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

/// Delete article file by id.
///
/// Delete an `ArticleFile` by its `FileId`. Api will return deleted
/// `FileId`.
///
#[utoipa::path(
    tag = ARTICLES_FILES,
    params(
        ("id" = uuid::Uuid, description = "File ID to delete", example = "123e4567-e89b-12d3-a456-426614174000")
    ),
)]
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

/// Find article tags by criteria.
///
/// Find article tags by criteria specified in query parameters. Api will return
/// a list of found `Tag` objects.
#[utoipa::path(
    tag = ARTICLES_TAGS
)]
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
