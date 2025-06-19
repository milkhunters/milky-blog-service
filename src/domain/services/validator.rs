use crate::domain::error::DomainError;
use crate::domain::models::{
    article::{ARTICLE_CONTENT_MAX, ARTICLE_TITLE_MAX, ARTICLE_TITLE_MIN},
    file::{FILE_MIME_TYPE_MAX, FILE_MIME_TYPE_REGEX, FILE_NAME_MAX},
    tag::{TAG_TITLE_MAX, TAG_TITLE_MIN},
    comment::COMMENT_CONTENT_MAX
};

pub fn validate_article_title(title: &str) -> Result<(), DomainError> {
    if title.is_empty() {
        return Err(DomainError::Validation("title cannot be empty".into()));
    }
    if title.len() > ARTICLE_TITLE_MAX {
        return Err(DomainError::Validation(format!(
            "title cannot be longer than {} characters", 
            ARTICLE_TITLE_MAX
        )));
    }
    if title.len() < ARTICLE_TITLE_MIN {
        return Err(DomainError::Validation(format!(
            "title must be at least {} characters long", 
            ARTICLE_TITLE_MIN
        )));
    }
    Ok(())
}

pub fn validate_article_content(content: &str) -> Result<(), DomainError> {
    if content.is_empty() {
        return Err(DomainError::Validation("content cannot be empty".into()));
    }
    if content.len() > ARTICLE_CONTENT_MAX {
        return Err(DomainError::Validation(format!(
            "content cannot be longer than {} characters", ARTICLE_CONTENT_MAX
        )));
    }
    Ok(())
}

pub fn validate_article_tag(tag: &str) -> Result<(), DomainError> {
    if tag.is_empty() {
        return Err(DomainError::Validation("tag cannot be empty".into()));
    }
    if tag.len() > TAG_TITLE_MAX {
        return Err(DomainError::Validation(format!(
            "tag cannot be longer than {} characters", TAG_TITLE_MAX
        )));
    }
    if tag.len() < TAG_TITLE_MIN {
        return Err(DomainError::Validation(format!(
            "tag must be at least {} characters long", TAG_TITLE_MIN
        )));
    }
    Ok(())
}

pub fn validate_article_tags(tags: &[String]) -> Result<(), DomainError> {
    if tags.is_empty() {
        return Err(DomainError::Validation("tags cannot be empty".into()));
    }
    for tag in tags {
        validate_article_tag(tag)?;
    }
    Ok(())
}

pub fn validate_comment_content(content: &str) -> Result<(), DomainError> {
    if content.is_empty() {
        return Err(DomainError::Validation("content cannot be empty".into()));
    }
    if content.len() > COMMENT_CONTENT_MAX {
        return Err(DomainError::Validation(format!(
            "content cannot be longer than {} characters", COMMENT_CONTENT_MAX
        )));
    }
    Ok(())
}

pub fn validate_filename(filename: &str) -> Result<(), DomainError> {
    if filename.is_empty() {
        return Err(DomainError::Validation("filename cannot be empty".into()));
    }
    if filename.len() > FILE_NAME_MAX {
        return Err(DomainError::Validation(format!(
            "filename cannot be longer than {} characters", FILE_NAME_MAX
        )));
    }
    Ok(())
}

pub fn validate_mime_content_type(mime_type: &str) -> Result<(), DomainError> {
    if mime_type.is_empty() {
        return Err(DomainError::Validation("MIME type cannot be empty".into()));
    }
    if mime_type.len() < FILE_MIME_TYPE_MAX {
        return Err(DomainError::Validation(format!(
            "MIME type cannot be longer than {} characters", FILE_MIME_TYPE_MAX
        )));
    }
    if FILE_MIME_TYPE_REGEX.is_match(mime_type) {
        return Err(DomainError::Validation(format!(
            "MIME type must match the regex: {}", FILE_MIME_TYPE_REGEX.as_str()
        )));
    }
    Ok(())
}
