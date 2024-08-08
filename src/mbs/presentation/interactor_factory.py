from abc import ABC, abstractmethod

from mbs.application.article.delete import DeleteArticle
from mbs.application.article.create import CreateArticle
from mbs.application.article.get import GetArticle
from mbs.application.article.get_range import GetArticleRange
from mbs.application.article.rate import RateArticle
from mbs.application.article.update import UpdateArticle

from mbs.application.comment.create import CreateComment
from mbs.application.comment.delete import DeleteComment
from mbs.application.comment.get import GetComment
from mbs.application.comment.get_by_article import GetArticleComments
from mbs.application.comment.update import UpdateComment

from mbs.application.file.confirm_article_file import ConfirmArticleFile
from mbs.application.file.create_article_file import CreateArticleFile
from mbs.application.file.delete_article_file import DeleteArticleFile
from mbs.application.file.get_article_file import GetArticleFile
from mbs.application.file.get_article_files import GetArticleFiles

from mbs.application.common.id_provider import IdProvider


class InteractorFactory(ABC):

    @abstractmethod
    def create_article(self, id_provider: IdProvider) -> CreateArticle:
        pass

    @abstractmethod
    def delete_article(self, id_provider: IdProvider) -> DeleteArticle:
        pass

    @abstractmethod
    def get_article(self, id_provider: IdProvider) -> GetArticle:
        pass

    @abstractmethod
    def get_article_range(self, id_provider: IdProvider) -> GetArticleRange:
        pass

    @abstractmethod
    def rate_article(self, id_provider: IdProvider) -> RateArticle:
        pass

    @abstractmethod
    def update_article(self, id_provider: IdProvider) -> UpdateArticle:
        pass

    @abstractmethod
    def create_comment(self, id_provider: IdProvider) -> CreateComment:
        pass

    @abstractmethod
    def delete_comment(self, id_provider: IdProvider) -> DeleteComment:
        pass

    @abstractmethod
    def get_comment(self, id_provider: IdProvider) -> GetComment:
        pass

    @abstractmethod
    def get_article_comments(self, id_provider: IdProvider) -> GetArticleComments:
        pass

    @abstractmethod
    def update_comment(self, id_provider: IdProvider) -> UpdateComment:
        pass

    @abstractmethod
    def create_article_file(self, id_provider: IdProvider) -> CreateArticleFile:
        pass

    @abstractmethod
    def delete_article_file(self, id_provider: IdProvider) -> DeleteArticleFile:
        pass

    @abstractmethod
    def confirm_article_file(self, id_provider: IdProvider) -> ConfirmArticleFile:
        pass

    @abstractmethod
    def get_article_files(self, id_provider: IdProvider) -> GetArticleFiles:
        pass

    @abstractmethod
    def get_article_file(self, id_provider: IdProvider) -> GetArticleFile:
        pass
