use serde::{Deserialize, Serialize};

#[derive(PartialEq, Clone, Serialize, Deserialize)]
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
