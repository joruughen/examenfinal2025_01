class Asignacion:
    def __init__(self, task_id, user_alias, rol):
        self.task_id = task_id
        self.user_alias = user_alias
        self.rol = rol
    
    def get_assignment_details(self):
        return {
            "task_id": self.task_id,
            "user_alias": self.user_alias,
            "rol": self.rol
        }
    
    def to_dict(self):
        return {
            "task_id": self.task_id,
            "user_alias": self.user_alias,
            "rol": self.rol
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            data["task_id"],
            data["user_alias"],
            data["rol"]
        )