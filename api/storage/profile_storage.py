from api.datatypes.user import User, UserCreate


#eventually the database queries / JSON write/read will be here.

class Profile_storage:
    def __init__(self):
        self.user_list: list[User] = []

    def get_all_users(self) -> list[User]:
        return self.user_list
    
    def get_user_by_name(self, user_name) -> User | None:
        for user in self.user_list:
            if user.name == user_name:
                return user
        return None
    
    def post_user(self, user: UserCreate) -> None:
        user: User = User(
            id=len(self.user_list),
            email=user.email,
            password=user.password,
            name=user.name,
            phone=user.phone,
            birth_year=user.birth_year
        )
        self.user_list.append(user)