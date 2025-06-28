use std::ops::Div;
use crate::domain::error::{DomainError, ValidationError};
use crate::domain::models::{
    article::{ARTICLE_CONTENT_MAX, ARTICLE_TITLE_MAX, ARTICLE_TITLE_MIN},
    file::{FILE_MIME_TYPE_MAX, FILE_MIME_TYPE_REGEX, FILE_NAME_MAX},
    tag::{TAG_TITLE_MAX, TAG_TITLE_MIN},
    comment::COMMENT_CONTENT_MAX
};

pub fn validate_article_title(title: &str) -> Result<(), DomainError> {
    if title.is_empty() {
        return Err(DomainError::Validation(
            ("title".into(), ValidationError::InvalidEmpty)
        ));
    }
    if !(ARTICLE_TITLE_MIN <= title.len() && title.len() <= ARTICLE_TITLE_MAX) {
        return Err(DomainError::Validation(
            ("title".into(), ValidationError::InvalidRange(ARTICLE_TITLE_MIN as i64, ARTICLE_TITLE_MAX as i64))
        ));
    }
    Ok(())
}

pub fn validate_article_content(content: &str) -> Result<(), DomainError> {
    if content.is_empty() {
        return Err(DomainError::Validation(
            ("content".into(), ValidationError::InvalidEmpty)
        ));
    }
    if !(ARTICLE_TITLE_MIN <= content.len() && content.len() <= ARTICLE_CONTENT_MAX) {
        return Err(DomainError::Validation(
            ("content".into(), ValidationError::InvalidRange(1, ARTICLE_CONTENT_MAX as i64))
        ));
    }
    Ok(())
}

pub fn validate_article_tags(tags: &[String]) -> Result<(), DomainError> {
    for (i, tag) in tags.iter().enumerate() {
        if tag.is_empty() {
            return Err(DomainError::Validation(
                (format!("tags_{i}"), ValidationError::InvalidEmpty)
            ));
        }
        if !(TAG_TITLE_MIN <= tag.len() && tag.len() <= TAG_TITLE_MAX) {
            return Err(DomainError::Validation(
                (format!("tags_{i}"), ValidationError::InvalidRange(TAG_TITLE_MIN as i64, TAG_TITLE_MAX as i64))
            ));
        }
    }
    Ok(())
}

pub fn validate_comment_content(content: &str) -> Result<(), DomainError> {
    if content.is_empty() {
        return Err(DomainError::Validation(
            ("content".into(), ValidationError::InvalidEmpty)
        ));
    }
    if !(1 <= content.len() && content.len() <= COMMENT_CONTENT_MAX) {
        return Err(DomainError::Validation(
            ("content".into(), ValidationError::InvalidRange(1, COMMENT_CONTENT_MAX as i64))
        ));
    }
    Ok(())
}

pub fn validate_filename(filename: &str) -> Result<(), DomainError> {
    if filename.is_empty() {
        return Err(DomainError::Validation(
            ("filename".into(), ValidationError::InvalidEmpty)
        ));
    }
    if !(1 <= filename.len() && filename.len() <= FILE_NAME_MAX) {
        return Err(DomainError::Validation(
            ("filename".into(), ValidationError::InvalidRange(1, FILE_NAME_MAX as i64))
        ));
    }
    Ok(())
}

pub fn validate_mime_content_type(content_type: &str) -> Result<(), DomainError> {
    if content_type.is_empty() {
        return Err(DomainError::Validation(
            ("mime_type".into(), ValidationError::InvalidEmpty)
        ));
    }
    if !(1 <= content_type.len() && content_type.len() <= FILE_MIME_TYPE_MAX) {
        return Err(DomainError::Validation(
            ("content_type".into(), ValidationError::InvalidRange(1, FILE_MIME_TYPE_MAX as i64))
        ));
    }
    if !FILE_MIME_TYPE_REGEX.is_match(content_type) {
        return Err(DomainError::Validation(
            ("content_type".into(), ValidationError::InvalidRegex(FILE_MIME_TYPE_REGEX.to_string()))
        ));
    }
    Ok(())
}


pub fn validate_page(page: u32) -> Result<(), DomainError> {
    if !(1 <= page && page <= 1_000_000) {
        return Err(DomainError::Validation(
            ("page".into(), ValidationError::InvalidRange(1, 1_000_000))
        ));
    }
    Ok(())
}

pub fn validate_per_page(per_page: u8) -> Result<(), DomainError> {
    if !(1 <= per_page && per_page <= 100) {
        return Err(DomainError::Validation(
            ("per_page".into(), ValidationError::InvalidRange(1, 100))
        ));
    }
    Ok(())
}