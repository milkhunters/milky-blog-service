use crate::app_state::AppState;
use crate::application::article::create::CreateArticleOutput;
use crate::application::article::find::FindArticleOutput;
use crate::application::article::get::GetArticleOutput;
use crate::application::article::tag::find::FindArticleTagsOutput;
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
use crate::domain::error::ValidationError;
use crate::domain::models::{
    article::ArticleId,
    article_state::ArticleState
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
use utoipa_actix_web::service_config::ServiceConfig;
use crate::application::article::file::create::CreateArticleFileOutput;

pub const ARTICLES: &str = "articles";
pub const ARTICLES_FILES: &str = "article files";
pub const ARTICLES_TAGS: &str = "article tags";

pub fn router(cfg: &mut ServiceConfig) {
    cfg.service(
        utoipa_actix_web::scope("/articles")
            .service(
                utoipa_actix_web::scope("/tags")
                    .service(find_article_tags)
            )
            .service(
                utoipa_actix_web::scope("/files")
                    .service(confirm_article_file)
                    .service(create_article_file)
                    .service(delete_article_file)
            )
            .service(create_article)
            .service(get_article)
            .service(find_article)
            .service(update_article)
            .service(delete_article)
            .service(rate_article)
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
        (status = 201, description = "Successfully created", body = CreateArticleOutput),
        (
            status = 400,
            description = "Validation error",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::validation(vec![("title".into(), ValidationError::InvalidEmpty)]))
        ),
        (
            status = 401,
            description = "Token invalid (ex. bad structure)",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::token_invalid("bad structure...".into()))
        ),
        (
            status = 401,
            description = "Token expired",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::token_expired())
        ),
        (
            status = 403,
            description = "Access denied",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::access_denied())
        )
    )
)]
#[post("")]
async fn create_article(
    input: web::Json<CreateArticleInput>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppState>,
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
    responses(
        (
            status = 204,
            description = "Successfully deleted",
            body = (),
            example = json!({})
        ),
        (
            status = 400,
            description = "Validation error",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::validation(vec![("id".into(), ValidationError::InvalidEmpty)]))
        ),
        (
            status = 401,
            description = "Token invalid (ex. bad structure)",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::token_invalid("bad structure...".into()))
        ),
        (
            status = 401,
            description = "Token expired",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::token_expired())
        ),
        (
            status = 403,
            description = "Access denied",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::access_denied())
        ),
        (
            status = 404,
            description = "Article not found",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::not_found("id".into()))
        )
    ),
    params(DeleteArticleInput)
)]
#[delete("/{id}")]
async fn delete_article(
    input: web::Path<DeleteArticleInput>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppState>,
    req: HttpRequest
) -> Result<HttpResponse, HttpError> {
    let id_provider = new_jwt_id_provider(&req, &app_config).await?;
    let output = ioc.delete_article(id_provider).execute(input.into_inner()).await?;
    Ok(HttpResponse::NoContent().json(output))
}

/// Get article by id.
///
/// Get an `Article` by its `ArticleId`. Api will return found `Article`.
///
#[utoipa::path(
    tag = ARTICLES, 
    responses(
        (status = 200, description = "Successfully", body = GetArticleOutput),
        (
            status = 400,
            description = "Validation error",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::validation(vec![("id".into(), ValidationError::InvalidEmpty)]))
        ),
        (
            status = 401,
            description = "Token invalid (ex. bad structure)",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::token_invalid("bad structure...".into()))
        ),
        (
            status = 401,
            description = "Token expired",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::token_expired())
        ),
        (
            status = 403,
            description = "Access denied",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::access_denied())
        ),
        (
            status = 404,
            description = "Article not found",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::not_found("id".into()))
        )
    ),
    params(GetArticleInput)
)]
#[get("/{id}")]
async fn get_article(
    input: web::Path<GetArticleInput>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppState>,
    req: HttpRequest
) -> Result<HttpResponse, HttpError> {
    let id_provider = new_jwt_id_provider(&req, &app_config).await?;
    let output = ioc.get_article(id_provider).execute(
        input.into_inner()
    ).await?;
    Ok(HttpResponse::Ok().json(output))
}

/// Find articles by criteria.
///
/// Find articles by criteria specified in query parameters. Api will return
/// a list of found `Article` objects.
#[utoipa::path(
    tag = ARTICLES,
    responses(
        (status = 200, description = "Article list", body = FindArticleOutput),
        (
            status = 400,
            description = "Validation error",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::validation(vec![("id".into(), ValidationError::InvalidEmpty)]))
        ),
        (
            status = 401,
            description = "Token invalid (ex. bad structure)",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::token_invalid("bad structure...".into()))
        ),
        (
            status = 401,
            description = "Token expired",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::token_expired())
        ),
        (
            status = 403,
            description = "Access denied",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::access_denied())
        ),
    ),
    params(FindArticleInput)
)]
#[get("")]
async fn find_article(
    input: web::Query<FindArticleInput>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppState>,
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
    responses(
        (
            status = 204,
            description = "Successfully rated",
            body = (),
            example = json!({})
        ),
        (
            status = 400,
            description = "Validation error",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::validation(vec![("id".into(), ValidationError::InvalidEmpty)]))
        ),
        (
            status = 401,
            description = "Token invalid (ex. bad structure)",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::token_invalid("bad structure...".into()))
        ),
        (
            status = 401,
            description = "Token expired",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::token_expired())
        ),
        (
            status = 403,
            description = "Access denied",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::access_denied())
        ),
        (
            status = 404,
            description = "Article not found",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::not_found("id".into()))
        )
    ),
    params(RateArticleInput)
)]
#[post("/rate/{id}/{state}")]
async fn rate_article(
    input: web::Path<RateArticleInput>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppState>,
    req: HttpRequest
) -> Result<HttpResponse, HttpError> {
    let id_provider = new_jwt_id_provider(&req, &app_config).await?;
    let output = ioc.rate_article(id_provider).execute(input.into_inner()).await?;
    Ok(HttpResponse::NoContent().json(output))
}


/// Update article by id.
///
/// Update an `Article` by its `ArticleId`. Api will return updated `Article`.
///
#[derive(Deserialize, ToSchema)]
pub struct UpdateArticleInput {
    #[schema(example = "Updated article title", value_type = String)]
    pub title: String,
    #[schema(example = "This is the content of the article.", value_type = String)]
    pub content: String,
    pub state: ArticleState,
    #[schema(example = uuid::Uuid::new_v4, value_type=Option<uuid::Uuid>)]
    pub poster: Option<uuid::Uuid>,
    #[schema(example = json!(vec!["js", "programming", "tips"]), value_type = Vec<String>)]
    pub tags: Vec<String>
}

/// Update an existing article.
///
/// Update an `Article` by its `ArticleId`. Api will return updated `Article`.
///
#[utoipa::path(
    tag = ARTICLES,
    responses(
        (
            status = 200,
            description = "Successfully updated",
            body = (),
            example = json!(())
        ),
        (
            status = 400,
            description = "Validation error",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::validation(vec![("id".into(), ValidationError::InvalidEmpty)]))
        ),
        (
            status = 401,
            description = "Token invalid (ex. bad structure)",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::token_invalid("bad structure...".into()))
        ),
        (
            status = 401,
            description = "Token expired",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::token_expired())
        ),
        (
            status = 403,
            description = "Access denied",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::access_denied())
        ),
        (
            status = 404,
            description = "Article or new poster not found",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::not_found("id".into()))
        )
    ),
    params(
        ("id" = uuid::Uuid, description = "article id", example = uuid::Uuid::new_v4),
    )
)]
#[put("/{id}")]
async fn update_article(
    id: web::Path<ArticleId>,
    body: web::Json<UpdateArticleInput>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppState>,
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
    responses(
        (
            status = 204,
            description = "Successfully confirmed",
            body = (),
            example = json!({})
        ),
        (
            status = 400,
            description = "Validation error",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::validation(vec![("id".into(), ValidationError::InvalidEmpty)]))
        ),
        (
            status = 401,
            description = "Token invalid (ex. bad structure)",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::token_invalid("bad structure...".into()))
        ),
        (
            status = 401,
            description = "Token expired",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::token_expired())
        ),
        (
            status = 403,
            description = "Access denied",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::access_denied())
        ),
        (
            status = 404,
            description = "FileId not found or file not uploaded",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::not_found("id".into()))
        )
    ),
    params(ConfirmArticleFileInput)
)]
#[post("/{id}/confirm")]
async fn confirm_article_file(
    input: web::Path<ConfirmArticleFileInput>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppState>,
    req: HttpRequest
) -> Result<HttpResponse, HttpError> {
    let id_provider = new_jwt_id_provider(&req, &app_config).await?;
    let output = ioc.confirm_article_file(id_provider).execute(input.into_inner()).await?;
    Ok(HttpResponse::NoContent().json(output))
}


/// Create new article file.
///
/// Post a new `ArticleFile` in request body as json to store it. Api will return
/// created `FileId` of the article file.
///
#[utoipa::path(
    tag = ARTICLES_FILES,
    responses(
        (
            status = 204,
            description = "Successfully created",
            body = CreateArticleFileOutput
        ),
        (
            status = 400,
            description = "Validation error",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::validation(vec![("filename".into(), ValidationError::InvalidEmpty)]))
        ),
        (
            status = 401,
            description = "Token invalid (ex. bad structure)",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::token_invalid("bad structure...".into()))
        ),
        (
            status = 401,
            description = "Token expired",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::token_expired())
        ),
        (
            status = 403,
            description = "Access denied",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::access_denied())
        ),
        (
            status = 404,
            description = "Article not found",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::not_found("article_id".into()))
        )
    ),
    params(ConfirmArticleFileInput)
)]
#[post("")]
async fn create_article_file(
    input: web::Json<CreateArticleFileInput>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppState>,
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
    responses(
        (
            status = 204,
            description = "Successfully deleted",
            body = (),
            example = json!({})
        ),
        (
            status = 400,
            description = "Validation error",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::validation(vec![("id".into(), ValidationError::InvalidEmpty)]))
        ),
        (
            status = 401,
            description = "Token invalid (ex. bad structure)",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::token_invalid("bad structure...".into()))
        ),
        (
            status = 401,
            description = "Token expired",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::token_expired())
        ),
        (
            status = 403,
            description = "Access denied",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::access_denied())
        ),
        (
            status = 404,
            description = "File not found",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::not_found("id".into()))
        )
    ),
    params(DeleteArticleFileInput)
)]
#[delete("/{id}")]
async fn delete_article_file(
    input: web::Path<DeleteArticleFileInput>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppState>,
    req: HttpRequest
) -> Result<HttpResponse, HttpError> {
    let id_provider = new_jwt_id_provider(&req, &app_config).await?;
    let output = ioc.delete_article_file(id_provider).execute(input.into_inner()).await?;
    Ok(HttpResponse::NoContent().json(output))
}

/// Find article tags by criteria.
///
/// Find article tags by criteria specified in query parameters. Api will return
/// a list of found `Tag` objects.
#[utoipa::path(
    tag = ARTICLES_TAGS,
    responses(
        (
            status = 204,
            description = "Successfully deleted",
            body = FindArticleTagsOutput
        ),
        (
            status = 400,
            description = "Validation error",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::validation(vec![("page".into(), ValidationError::InvalidEmpty)]))
        ),
        (
            status = 401,
            description = "Token invalid (ex. bad structure)",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::token_invalid("bad structure...".into()))
        ),
        (
            status = 401,
            description = "Token expired",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::token_expired())
        ),
        (
            status = 403,
            description = "Access denied",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::access_denied())
        )
    ),
    params(FindArticleTagsInput)
)]
#[get("")]
async fn find_article_tags(
    input: web::Query<FindArticleTagsInput>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppState>,
    req: HttpRequest
) -> Result<HttpResponse, HttpError> {
    let id_provider = new_jwt_id_provider(&req, &app_config).await?;
    let output = ioc.find_article_tags(id_provider).execute(input.into_inner()).await?;
    Ok(HttpResponse::Ok().json(output))
}
