use crate::application::{
    common::id_provider::IdProvider,
    article::{
        create::CreateArticle,
        delete::DeleteArticle,
        find::FindArticle,
        get::GetArticle,
        rate::RateArticle,
        update::UpdateArticle,
        file::{
            confirm::ConfirmArticleFile,
            create::CreateArticleFile,
            delete::DeleteArticleFile
        },
        tag::find::FindArticleTags
    },
    comment::{
        create::CreateComment,
        delete::DeleteComment,
        get::GetComment,
        get_tree::GetCommentsTree,
        rate::RateComment,
        update::UpdateComment
    }
};

pub trait InteractorFactory: Send + Sync {
    fn create_article<'interactor>(&'interactor self, id_provider: Box<dyn IdProvider>) -> CreateArticle<'interactor>;
    fn delete_article<'interactor>(&'interactor self, id_provider: Box<dyn IdProvider>) -> DeleteArticle<'interactor>;
    fn find_article<'interactor>(&'interactor self, id_provider: Box<dyn IdProvider>) -> FindArticle<'interactor>;
    fn get_article<'interactor>(&'interactor self, id_provider: Box<dyn IdProvider>) -> GetArticle<'interactor>;
    fn rate_article<'interactor>(&'interactor self, id_provider: Box<dyn IdProvider>) -> RateArticle<'interactor>;
    fn update_article<'interactor>(&'interactor self, id_provider: Box<dyn IdProvider>) -> UpdateArticle<'interactor>;
    fn create_article_file<'interactor>(&'interactor self, id_provider: Box<dyn IdProvider>) -> CreateArticleFile<'interactor>;
    fn confirm_article_file<'interactor>(&'interactor self, id_provider: Box<dyn IdProvider>) -> ConfirmArticleFile<'interactor>;
    fn delete_article_file<'interactor>(&'interactor self, id_provider: Box<dyn IdProvider>) -> DeleteArticleFile<'interactor>;
    fn find_article_tags<'interactor>(&'interactor self, id_provider: Box<dyn IdProvider>) -> FindArticleTags<'interactor>;
    // ---------------------------------------------------------------------------------------------
    fn create_comment<'interactor>(&'interactor self, id_provider: Box<dyn IdProvider>) -> CreateComment<'interactor>;
    fn delete_comment<'interactor>(&'interactor self, id_provider: Box<dyn IdProvider>) -> DeleteComment<'interactor>;
    fn get_comment<'interactor>(&'interactor self, id_provider: Box<dyn IdProvider>) -> GetComment<'interactor>;
    fn get_comments_tree<'interactor>(&'interactor self, id_provider: Box<dyn IdProvider>) -> GetCommentsTree<'interactor>;
    fn rate_comment<'interactor>(&'interactor self, id_provider: Box<dyn IdProvider>) -> RateComment<'interactor>;
    fn update_comment<'interactor>(&'interactor self, id_provider: Box<dyn IdProvider>) -> UpdateComment<'interactor>;
}