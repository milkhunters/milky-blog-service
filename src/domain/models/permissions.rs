

#[derive(PartialEq)]
pub enum Permission {
    CreateArticle,
    GetAnyArticle,
    GetPubArticle,
    GetSelfArticle,
    UpdateAnyArticle,
    UpdateSelfArticle,
    DeleteAnyArticle,
    DeleteSelfArticle,
    RateArticle,

    CreateComment,
    GetAnyComment,
    GetPubComment,
    UpdateAnyComment,
    UpdateSelfComment,
    DeleteAnyComment,
    DeleteSelfComment,
    RateComment
}
