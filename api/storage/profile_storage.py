from api.datatypes.user import User, UserCreate


#eventually the database queries / JSON write/read will be here.

class Profile_storage:
    def __init__(self):
        self.user_list: list[User] = [
            {
                "id": 1,
                "username": "cindy.leenders42",
                "password": "6b37d1ec969838d29cb611deaff50a6b",
                "name": "Cindy Leenders",
                "email": "cindyleenders@upcmail.nl",
                "phone": "+310792215694",
                "role": "USER",
            },
            {
                "id": 2,
                "username": "gijsdegraaf",
                "password": "1b1f4e666f54b55ccd2c701ec3435dba",
                "name": "Gijs de Graaf",
                "email": "gijsdegraaf@hotmail.com",
                "phone": "+310698086312",
                "role": "ADMIN",
            },
            {
                "id": 3,
                "username": "iris.dekker70",
                "password": "bf7ea48e511957eccb06a832ba6ae6c9",
                "name": "Iris Dekker",
                "email": "iris.dekker70@yahoo.com",
                "phone": "+310207093519",
                "role": "USER",
            },
        ]

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