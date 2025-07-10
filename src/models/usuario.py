class Usuario:
    def __init__(self, alias, nombre):
        self.alias = alias
        self.nombre = nombre
        self.tareas_asignadas = []
    
    def get_user_info(self):
        return {
            "alias": self.alias,
            "nombre": self.nombre,
            "tareas_asignadas": self.tareas_asignadas
        }
    
    def to_dict(self):
        return {
            "alias": self.alias,
            "nombre": self.nombre,
            "tareas_asignadas": self.tareas_asignadas
        }
    
    @classmethod
    def from_dict(cls, data):
        usuario = cls(data["alias"], data["nombre"])
        usuario.tareas_asignadas = data.get("tareas_asignadas", [])
        return usuario