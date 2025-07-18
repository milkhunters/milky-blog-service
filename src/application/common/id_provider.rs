use crate::domain::models::{
    permissions::Permission,
    user_id::UserId,
    user_state::UserState
};


pub trait IdProvider {
    fn user_id(&self) -> &UserId;
    fn user_state(&self) -> &UserState;
    fn permissions(&self) -> &Vec<Permission>;
}
