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

pub trait InteractorFactory {
    fn create_article(&self, id_provider: Box<dyn IdProvider>) -> CreateArticle;
    fn delete_article(&self, id_provider: Box<dyn IdProvider>) -> DeleteArticle;
    fn find_article(&self, id_provider: Box<dyn IdProvider>) -> FindArticle;
    fn get_article(&self, id_provider: Box<dyn IdProvider>) -> GetArticle;
    fn rate_article(&self, id_provider: Box<dyn IdProvider>) -> RateArticle;
    fn update_article(&self, id_provider: Box<dyn IdProvider>) -> UpdateArticle;
    fn create_article_file(&self, id_provider: Box<dyn IdProvider>) -> CreateArticleFile;
    fn confirm_article_file(&self, id_provider: Box<dyn IdProvider>) -> ConfirmArticleFile;
    fn delete_article_file(&self, id_provider: Box<dyn IdProvider>) -> DeleteArticleFile;
    fn find_article_tags(&self, id_provider: Box<dyn IdProvider>) -> FindArticleTags;
    // ---------------------------------------------------------------------------------------------
    fn create_comment(&self, id_provider: Box<dyn IdProvider>) -> CreateComment;
    fn delete_comment(&self, id_provider: Box<dyn IdProvider>) -> DeleteComment;
    fn get_comment(&self, id_provider: Box<dyn IdProvider>) -> GetComment;
    fn get_comments_tree(&self, id_provider: Box<dyn IdProvider>) -> GetCommentsTree;
    fn rate_comment(&self, id_provider: Box<dyn IdProvider>) -> RateComment;
    fn update_comment(&self, id_provider: Box<dyn IdProvider>) -> UpdateComment;
}