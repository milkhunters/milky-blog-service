use crate::domain::error::DomainError;
use crate::domain::models::{
    permissions::Permission,
    user_state::UserState
};
use crate::domain::models::article_state::ArticleState;
use crate::domain::models::comment_state::CommentState;
use crate::domain::models::user_id::UserId;

pub fn ensure_can_create_article(
    permissions: &Vec<Permission>,
    user_state: &UserState,
) -> Result<(), DomainError> {
    if user_state != &UserState::Active {
        return Err(DomainError::Access);
    }
    if !permissions.contains(&Permission::CreateArticle) {
        return Err(DomainError::Access);
    }
    Ok(())
}

pub fn ensure_can_update_article(
    permissions: &Vec<Permission>,
    user_state: &UserState,
    user_id: &UserId,
    article_author_id: &UserId
) -> Result<(), DomainError> {
    if user_state != &UserState::Active {
        return Err(DomainError::Access);
    }

    if permissions.contains(&Permission::UpdateSelfArticle) && user_id == article_author_id {
        return Ok(())
    }

    if permissions.contains(&Permission::UpdateAnyArticle) {
        return Ok(());
    }

    Err(DomainError::Access)
}

pub fn ensure_can_delete_article(
    permissions: &Vec<Permission>,
    user_state: &UserState,
    user_id: &UserId,
    article_author_id: &UserId,
) -> Result<(), DomainError> {
    if user_state != &UserState::Active {
        return Err(DomainError::Access);
    }

    if permissions.contains(&Permission::DeleteSelfArticle) && user_id == article_author_id {
        return Ok(())
    }

    if permissions.contains(&Permission::DeleteAnyArticle) {
        return Ok(());
    }

    Err(DomainError::Access)
}

pub fn ensure_can_get_article(
    permissions: &Vec<Permission>,
    user_state: &UserState,
    article_state: &ArticleState,
    article_author_id: &UserId,
    user_id: &UserId,
) -> Result<(), DomainError> {
    if user_state != &UserState::Active {
        return Err(DomainError::Access);
    }

    if permissions.contains(&Permission::GetAnyArticle) {
        return Ok(());
    }
    
    if permissions.contains(&Permission::GetPubArticle) && article_state == &ArticleState::Published {
        return Ok(());
    }

    if permissions.contains(&Permission::GetSelfArticle) && user_id == article_author_id {
        return Ok(());
    }
    
    Err(DomainError::Access)
}

pub fn ensure_can_find_articles(
    permissions: &Vec<Permission>,
    user_state: &UserState,
    article_state: &ArticleState,
    article_author_id: &Option<UserId>,
    user_id: &UserId,
) -> Result<(), DomainError> {
    if user_state != &UserState::Active {
        return Err(DomainError::Access);
    }

    if permissions.contains(&Permission::FindAnyArticle) {
        return Ok(());
    }

    if permissions.contains(&Permission::FindPubArticle) && article_state == &ArticleState::Published {
        return Ok(());
    }
    
    if let Some(author_id) = article_author_id {
        if permissions.contains(&Permission::FindSelfArticle) && user_id == author_id {
            return Ok(());
        }
    }

    Err(DomainError::Access)
}

pub fn ensure_can_rate_article(
    permissions: &Vec<Permission>,
    user_state: &UserState,
    article_state: &ArticleState,
) -> Result<(), DomainError> {
    if user_state != &UserState::Active {
        return Err(DomainError::Access);
    }
    if !permissions.contains(&Permission::RateArticle) {
        return Err(DomainError::Access);
    }
    if article_state != &ArticleState::Published {
        return Err(DomainError::Access);
    }
    Ok(())
}

pub fn ensure_can_create_comment(
    permissions: &Vec<Permission>,
    user_state: &UserState,
    article_state: &ArticleState
) -> Result<(), DomainError> {
    if user_state != &UserState::Active {
        return Err(DomainError::Access);
    }
    if !permissions.contains(&Permission::CreateComment) {
        return Err(DomainError::Access);
    }
    if article_state != &ArticleState::Published {
        return Err(DomainError::Access);
    }
    Ok(())
}
pub fn ensure_can_update_comment(
    permissions: &Vec<Permission>,
    user_state: &UserState,
    user_id: &UserId,
    comment_author_id: &UserId,
    comment_state: &CommentState,
) -> Result<(), DomainError> {
    if user_state != &UserState::Active {
        return Err(DomainError::Access);
    }
    if permissions.contains(&Permission::UpdateSelfComment) && 
       user_id == comment_author_id &&
       comment_state == &CommentState::Published 
    {
        return Ok(());
    }
    if permissions.contains(&Permission::UpdateAnyComment) {
        return Ok(());
    }
    Err(DomainError::Access)
}

pub fn ensure_can_delete_comment(
    permissions: &Vec<Permission>,
    user_state: &UserState,
    user_id: &UserId,
    comment_author_id: &UserId,
    comment_state: &CommentState,
) -> Result<(), DomainError> {
    if user_state != &UserState::Active {
        return Err(DomainError::Access);
    }
    if comment_state == &CommentState::Deleted {
        return Err(DomainError::Access);
    }
    if permissions.contains(&Permission::DeleteSelfComment) && user_id == comment_author_id {
        return Ok(());
    }
    if permissions.contains(&Permission::DeleteAnyComment) {
        return Ok(());
    }
    Err(DomainError::Access)
}

pub fn ensure_can_get_comment(
    permissions: &Vec<Permission>,
    user_state: &UserState,
    comment_state: &CommentState,
    article_state: &ArticleState,
) -> Result<(), DomainError> {
    if user_state != &UserState::Active {
        return Err(DomainError::Access);
    }

    if permissions.contains(&Permission::GetAnyComment) {
        return Ok(());
    }

    if permissions.contains(&Permission::GetPubComment) && 
       comment_state == &CommentState::Published && 
       article_state != &ArticleState::Draft 
    {
        return Ok(());
    }

    Err(DomainError::Access)
}

pub fn ensure_can_rate_comment(
    permissions: &Vec<Permission>,
    user_state: &UserState,
    comment_state: &CommentState,
) -> Result<(), DomainError> {
    if user_state != &UserState::Active {
        return Err(DomainError::Access);
    }
    if comment_state != &CommentState::Published {
        return Err(DomainError::Access);
    }
    if !permissions.contains(&Permission::RateComment) {
        return Err(DomainError::Access);
    }
    Ok(())
}

