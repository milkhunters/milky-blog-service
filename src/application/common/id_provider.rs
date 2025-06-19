use crate::domain::models::permissions::Permission;
use crate::domain::models::user_id::UserId;
use crate::domain::models::user_state::UserState;

pub trait IdProvider {
    fn user_id(&self) -> &UserId;
    fn user_state(&self) -> &UserState;
    fn permissions(&self) -> &Vec<Permission>;
    fn is_auth(&self) -> bool; // TODO REMOVE IF NOT USED
}
