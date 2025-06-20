

#[derive(PartialEq)]
pub enum Permission {
    CreateArticle,
    GetAnyArticle,
    GetPubArticle,
    GetSelfArticle,
    FindAnyArticle,
    FindPubArticle,
    FindSelfArticle,
    UpdateAnyArticle,
    UpdateSelfArticle,
    DeleteAnyArticle,
    DeleteSelfArticle,
    RateArticle,
    
    FindTag,

    CreateComment,
    GetAnyComment,
    GetPubComment,
    UpdateAnyComment,
    UpdateSelfComment,
    DeleteAnyComment,
    DeleteSelfComment,
    RateComment
}
