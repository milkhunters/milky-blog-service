use crate::application::article::create::CreateArticle;
use crate::application::article::delete::DeleteArticle;
use crate::application::article::file::confirm::ConfirmArticleFile;
use crate::application::article::file::create::CreateArticleFile;
use crate::application::article::file::delete::DeleteArticleFile;
use crate::application::article::find::FindArticle;
use crate::application::article::get::GetArticle;
use crate::application::article::rate::RateArticle;
use crate::application::article::tag::find::FindArticleTags;
use crate::application::article::update::UpdateArticle;
use crate::application::comment::create::CreateComment;
use crate::application::comment::delete::DeleteComment;
use crate::application::comment::get::GetComment;
use crate::application::comment::get_tree::GetCommentsTree;
use crate::application::comment::rate::RateComment;
use crate::application::comment::update::UpdateComment;
use crate::application::common::article_gateway::ArticleGateway;
use crate::application::common::comment_gateway::CommentGateway;
use crate::application::common::file_map_gateway::FileMapGateway;
use crate::application::common::file_storage_gateway::FileStorageGateway;
use crate::application::common::id_provider::IdProvider;
use crate::application::common::tag_gateway::TagGateway;
use crate::presentation::interactor_factory::InteractorFactory;


pub struct IoC {
    pub article_gateway: Box<dyn ArticleGateway>,
    pub comment_gateway: Box<dyn CommentGateway>,
    pub file_map_gateway: Box<dyn FileMapGateway>,
    pub tag_gateway: Box<dyn TagGateway>,
    pub file_storage_gateway: Box<dyn FileStorageGateway>,
}

impl IoC {
    pub fn new(
        article_gateway: Box<dyn ArticleGateway>,
        comment_gateway: Box<dyn CommentGateway>,
        file_map_gateway: Box<dyn FileMapGateway>,
        tag_gateway: Box<dyn TagGateway>,
        file_storage_gateway: Box<dyn FileStorageGateway>,
    ) -> Self {
        Self {
            article_gateway,
            comment_gateway,
            file_map_gateway,
            tag_gateway,
            file_storage_gateway,
        }
    }
}

impl InteractorFactory for IoC {
    fn create_article<'interactor>(&'interactor self, id_provider: Box<dyn IdProvider>) -> CreateArticle<'interactor> {
        CreateArticle {
            id_provider,
            article_writer: self.article_gateway.as_ref(),
        }
    }

    fn delete_article<'interactor>(&'interactor self, id_provider: Box<dyn IdProvider>) -> DeleteArticle<'interactor> {
        DeleteArticle {
            id_provider,
            article_gateway: self.article_gateway.as_ref(),
            comment_remover: self.comment_gateway.as_ref(),
        }
    }

    fn find_article<'interactor>(&'interactor self, id_provider: Box<dyn IdProvider>) -> FindArticle<'interactor> {
        FindArticle {
            id_provider,
            article_gateway: self.article_gateway.as_ref(),
            file_map_reader: self.file_map_gateway.as_ref(),
            file_storage_linker: self.file_storage_gateway.as_ref(),
        }
    }

    fn get_article<'interactor>(&'interactor self, id_provider: Box<dyn IdProvider>) -> GetArticle<'interactor> {
        GetArticle {
            id_provider,
            article_gateway: self.article_gateway.as_ref(),
            file_map_reader: self.file_map_gateway.as_ref(),
            file_storage_linker: self.file_storage_gateway.as_ref()
        }
    }

    fn rate_article<'interactor>(&'interactor self, id_provider: Box<dyn IdProvider>) -> RateArticle<'interactor> {
        RateArticle {
            id_provider,
            article_gateway: self.article_gateway.as_ref(),
        }
    }

    fn update_article<'interactor>(&'interactor self, id_provider: Box<dyn IdProvider>) -> UpdateArticle<'interactor> {
        UpdateArticle {
            id_provider,
            article_gateway: self.article_gateway.as_ref(),
            file_map_gateway: self.file_map_gateway.as_ref(),
        }
    }

    fn create_article_file<'interactor>(&'interactor self, id_provider: Box<dyn IdProvider>) -> CreateArticleFile<'interactor> {
        CreateArticleFile {
            id_provider,
            article_reader: self.article_gateway.as_ref(),
            file_map_gateway: self.file_map_gateway.as_ref(),
            file_storage_linker: self.file_storage_gateway.as_ref(),
        }
    }

    fn confirm_article_file<'interactor>(&'interactor self, id_provider: Box<dyn IdProvider>) -> ConfirmArticleFile<'interactor> {
        ConfirmArticleFile {
            id_provider,
            article_reader: self.article_gateway.as_ref(),
            file_map_gateway: self.file_map_gateway.as_ref(),
            file_storage_reader: self.file_storage_gateway.as_ref(),
        }
    }

    fn delete_article_file<'interactor>(&'interactor self, id_provider: Box<dyn IdProvider>) -> DeleteArticleFile<'interactor> {
        DeleteArticleFile {
            id_provider,
            article_reader: self.article_gateway.as_ref(),
            file_map_gateway: self.file_map_gateway.as_ref(),
            file_storage_remover: self.file_storage_gateway.as_ref(),
        }
    }

    fn find_article_tags<'interactor>(&'interactor self, id_provider: Box<dyn IdProvider>) -> FindArticleTags<'interactor> {
        FindArticleTags {
            id_provider,
            tag_reader: self.tag_gateway.as_ref(),
        }
    }

    fn create_comment<'interactor>(&'interactor self, id_provider: Box<dyn IdProvider>) -> CreateComment<'interactor> {
        CreateComment {
            id_provider,
            comment_gateway: self.comment_gateway.as_ref(),
            article_reader: self.article_gateway.as_ref(),
        }
    }

    fn delete_comment<'interactor>(&'interactor self, id_provider: Box<dyn IdProvider>) -> DeleteComment<'interactor> {
        DeleteComment {
            id_provider,
            comment_gateway: self.comment_gateway.as_ref(),
            article_reader: self.article_gateway.as_ref(),
        }
    }

    fn get_comment<'interactor>(&'interactor self, id_provider: Box<dyn IdProvider>) -> GetComment<'interactor> {
        GetComment {
            id_provider,
            comment_gateway: self.comment_gateway.as_ref(),
            article_reader: self.article_gateway.as_ref(),
        }
    }

    fn get_comments_tree<'interactor>(&'interactor self, id_provider: Box<dyn IdProvider>) -> GetCommentsTree<'interactor> {
        GetCommentsTree {
            id_provider,
            comment_gateway: self.comment_gateway.as_ref(),
            article_reader: self.article_gateway.as_ref(),
        }
    }

    fn rate_comment<'interactor>(&'interactor self, id_provider: Box<dyn IdProvider>) -> RateComment<'interactor> {
        RateComment {
            id_provider,
            comment_gateway: self.comment_gateway.as_ref(),
            article_reader: self.article_gateway.as_ref(),
        }
    }

    fn update_comment<'interactor>(&'interactor self, id_provider: Box<dyn IdProvider>) -> UpdateComment<'interactor> {
        UpdateComment {
            id_provider,
            comment_gateway: self.comment_gateway.as_ref(),
            article_reader: self.article_gateway.as_ref(),
        }
    }
}


