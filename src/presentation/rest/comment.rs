use crate::app_state::AppState;
use crate::application::comment::create::CreateCommentOutput;
use crate::application::comment::get::GetCommentOutput;
use crate::application::comment::get_tree::GetCommentsTreeOutput;
use crate::application::{
    comment::{
        create::CreateCommentInput,
        delete::DeleteCommentInput,
        get::GetCommentInput,
        get_tree::GetCommentsTreeInput,
        rate::RateCommentInput,
        update::UpdateCommentInput as UpdateCommentInputInt
    },
    common::interactor::Interactor
};
use crate::domain::error::ValidationError;
use crate::domain::models::comment::CommentId;
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

pub const COMMENTS: &str = "comments";

pub fn router(cfg: &mut ServiceConfig) {
    cfg.service(
        utoipa_actix_web::scope("/comments")
            .service(create_comment)
            .service(get_comment)
            .service(get_tree_comment)
            .service(update_comment)
            .service(delete_comment)
            .service(rate_comment)
    );
}



/// Create new comment.
///
#[utoipa::path(
    tag = COMMENTS,
    responses(
        (status = 201, description = "Successfully created", body = CreateCommentOutput),
        (
            status = 400,
            description = "Validation error",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::validation(vec![("content".into(), ValidationError::InvalidEmpty)]))
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
    )
)]
#[post("")]
async fn create_comment(
    input: web::Json<CreateCommentInput>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppState>,
    req: HttpRequest
) -> Result<HttpResponse, HttpError> {
    let id_provider = new_jwt_id_provider(&req, &app_config).await?;
    let output = ioc.create_comment(id_provider).execute(input.into_inner()).await?;
    Ok(HttpResponse::Created().json(output))
}


/// Delete comment by ID.
///
#[utoipa::path(
    tag = COMMENTS,
    responses(
        (status = 204, description = "Successfully created"),
        (
            status = 400,
            description = "Validation error",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::validation(vec![("content".into(), ValidationError::InvalidEmpty)]))
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
            description = "Comment not found",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::not_found("id".into()))
        )
    ),
    params(DeleteCommentInput)
)]
#[delete("/{id}")]
async fn delete_comment(
    input: web::Path<DeleteCommentInput>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppState>,
    req: HttpRequest
) -> Result<HttpResponse, HttpError> {
    let id_provider = new_jwt_id_provider(&req, &app_config).await?;
    let output = ioc.delete_comment(id_provider).execute(input.into_inner()).await?;
    Ok(HttpResponse::NoContent().json(output))
}


/// Get comment by ID.
///
#[utoipa::path(
    tag = COMMENTS,
    responses(
        (status = 200, description = "Successfully created", body = GetCommentOutput),
        (
            status = 400,
            description = "Validation error",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::validation(vec![("content".into(), ValidationError::InvalidEmpty)]))
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
            description = "Comment not found",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::not_found("id".into()))
        )
    ),
    params(GetCommentInput)
)]
#[get("/{id}")]
async fn get_comment(
    input: web::Path<GetCommentInput>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppState>,
    req: HttpRequest
) -> Result<HttpResponse, HttpError> {
    let id_provider = new_jwt_id_provider(&req, &app_config).await?;
    let output = ioc.get_comment(id_provider).execute(input.into_inner()).await?;
    Ok(HttpResponse::Ok().json(output))
}

/// Get article comments tree.
///
#[utoipa::path(
    tag = COMMENTS,
    responses(
        (status = 200, description = "Successfully created", body = GetCommentsTreeOutput),
        (
            status = 400,
            description = "Validation error",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::validation(vec![("article_id".into(), ValidationError::InvalidEmpty)]))
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
    params(GetCommentsTreeInput)
)]
#[get("")]
async fn get_tree_comment(
    input: web::Query<GetCommentsTreeInput>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppState>,
    req: HttpRequest
) -> Result<HttpResponse, HttpError> {
    let id_provider = new_jwt_id_provider(&req, &app_config).await?;
    let output = ioc.get_comments_tree(id_provider).execute(input.into_inner()).await?;
    Ok(HttpResponse::Ok().json(output))
}


/// Get article comments tree.
///
#[utoipa::path(
    tag = COMMENTS,
    responses(
        (status = 204, description = "Successfully"),
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
            description = "Comment not found",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::not_found("id".into()))
        )
    ),
    params(RateCommentInput)
)]
#[post("rate/{id}/{state}")]
async fn rate_comment(
    input: web::Path<RateCommentInput>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppState>,
    req: HttpRequest
) -> Result<HttpResponse, HttpError> {
    let id_provider = new_jwt_id_provider(&req, &app_config).await?;
    let output = ioc.rate_comment(id_provider).execute(input.into_inner()).await?;
    Ok(HttpResponse::NoContent().json(output))
}


#[derive(Deserialize, ToSchema)]
pub struct UpdateCommentInput {
    #[schema(example = "This is a message content")]
    pub content: String,
}

/// Update comment by ID.
///
#[utoipa::path(
    tag = COMMENTS,
    responses(
        (
            status = 204,
            description = "Successfully updated",
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
            description = "Comment not found",
            body = HttpErrorModel,
            example = json!(HttpErrorModel::not_found("id".into()))
        )
    ),
    params(
        ("id", description = "Comment ID", example = uuid::Uuid::new_v4),
    )
)]
#[put("/{id}")]
async fn update_comment(
    id: web::Path<CommentId>,
    body: web::Json<UpdateCommentInput>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppState>,
    req: HttpRequest
) -> Result<HttpResponse, HttpError> {
    let body = body.into_inner();
    let input = UpdateCommentInputInt {
        id: id.into_inner(),
        content: body.content,
    };
    let id_provider = new_jwt_id_provider(&req, &app_config).await?;
    let output = ioc.update_comment(id_provider).execute(input).await?;
    Ok(HttpResponse::NoContent().json(output))
}
