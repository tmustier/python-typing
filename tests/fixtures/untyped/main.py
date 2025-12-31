# Fixture: Completely untyped Python code
# Expected errors: ~8-10 in strict mode

def get_user(user_id):
    """Missing parameter and return type annotations."""
    return {"id": user_id, "name": "Alice"}


def process_items(items):
    """Missing annotations, uses list operations."""
    result = []
    for item in items:
        result.append(item.upper())
    return result


class UserService:
    def __init__(self, db):
        self.db = db
        self.cache = {}
    
    def find(self, user_id):
        if user_id in self.cache:
            return self.cache[user_id]
        user = self.db.get(user_id)
        self.cache[user_id] = user
        return user


def main():
    service = UserService(None)
    user = service.find(1)
    print(user)
