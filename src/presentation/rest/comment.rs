use crate::application::{
    comment::{
        create::CreateCommentInput,
        delete::DeleteCommentInput,
        get::GetCommentInput,
        get_tree::GetCommentsTreeInput,
        rate::RateCommentInput,
        update::UpdateCommentInput
    },
    common::interactor::Interactor
};
use crate::domain::models::comment::CommentId;
use crate::presentation::{
    interactor_factory::InteractorFactory,
    rest::error::HttpError,
    rest::id_provider::new_jwt_id_provider
};
use crate::app_state::AppConfig;
use actix_web::{delete, get, post, put, web, HttpRequest, HttpResponse};
use serde::Deserialize;
use crate::domain::models::rate_state::RateState;

pub fn router(cfg: &mut web::ServiceConfig) {
    cfg.service(
        web::scope("/comments")
            .service(create_comment)
            .service(get_comment)
            .service(get_tree_comment)
            .service(update_comment)
            .service(delete_comment)
            .service(rate_comment)
    );
}


#[post("")]
async fn create_comment(
    input: web::Json<CreateCommentInput>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppConfig>,
    req: HttpRequest
) -> Result<HttpResponse, HttpError> {
    let id_provider = new_jwt_id_provider(&req, &app_config).await?;
    let output = ioc.create_comment(id_provider).execute(input.into_inner()).await?;
    Ok(HttpResponse::Ok().json(output))
}

#[delete("/{id}")]
async fn delete_comment(
    input: web::Path<CommentId>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppConfig>,
    req: HttpRequest
) -> Result<HttpResponse, HttpError> {
    let id_provider = new_jwt_id_provider(&req, &app_config).await?;
    let output = ioc.delete_comment(id_provider).execute(
        DeleteCommentInput { id: input.into_inner() }
    ).await?;
    Ok(HttpResponse::Ok().json(output))
}

#[get("{id}")]
async fn get_comment(
    input: web::Path<CommentId>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppConfig>,
    req: HttpRequest
) -> Result<HttpResponse, HttpError> {
    let id_provider = new_jwt_id_provider(&req, &app_config).await?;
    let output = ioc.get_comment(id_provider).execute(
        GetCommentInput{ id: input.into_inner()}
    ).await?;
    Ok(HttpResponse::Ok().json(output))
}

#[get("")]
async fn get_tree_comment(
    input: web::Query<GetCommentsTreeInput>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppConfig>,
    req: HttpRequest
) -> Result<HttpResponse, HttpError> {
    let id_provider = new_jwt_id_provider(&req, &app_config).await?;
    let output = ioc.get_comments_tree(id_provider).execute(input.into_inner()).await?;
    Ok(HttpResponse::Ok().json(output))
}

#[post("rate/{id}/{state}")]
async fn rate_comment(
    input: web::Path<CommentId>,
    state: web::Path<RateState>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppConfig>,
    req: HttpRequest
) -> Result<HttpResponse, HttpError> {
    let id_provider = new_jwt_id_provider(&req, &app_config).await?;
    let output = ioc.rate_comment(id_provider).execute(
        RateCommentInput { id: input.into_inner(), state: state.into_inner() }
    ).await?;
    Ok(HttpResponse::Ok().json(output))
}


#[derive(Deserialize)]
pub struct UpdateCommentJson {
    pub content: String,
}

#[put("{id}")]
async fn update_comment(
    id: web::Path<CommentId>,
    body: web::Json<UpdateCommentJson>,
    ioc: web::Data<dyn InteractorFactory>,
    app_config: web::Data<AppConfig>,
    req: HttpRequest
) -> Result<HttpResponse, HttpError> {
    let body = body.into_inner();
    let input = UpdateCommentInput {
        id: id.into_inner(),
        content: body.content.clone(),
    };
    let id_provider = new_jwt_id_provider(&req, &app_config).await?;
    let output = ioc.update_comment(id_provider).execute(input).await?;
    Ok(HttpResponse::Ok().json(output))
}
