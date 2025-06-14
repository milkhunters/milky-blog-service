

#[derive(PartialEq)]
pub enum Permission {
    CreateArticle,
    UpdateSelfArticle,
    UpdateAnyArticle,
    DeleteSelfArticle,
    DeleteAnyArticle,
    
    GetSelfArticle,
    GetPubArticle,
    GetAnyArticle,
    
    RateArticle,
    UploadArticleFile,
    DeleteArticleFile,

    CreateComment,
    GetComment,
    GetPublishedComment,
    UpdateComment,
    UpdateSelfComment,
    DeleteComment,
    DeleteSelfComment,
    RateComment,
    UploadCommentFile,
    DeleteCommentFile,

    GetTag,
    GetTagStats
}
