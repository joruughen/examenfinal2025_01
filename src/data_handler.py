import json
from models.usuario import Usuario
from models.tarea import Tarea
from models.asignacion import Asignacion


class DataHandler:
    def __init__(self, filename='data.json'):
        self.filename = filename
        self.tasks = []
        self.users = []
        self.assignments = []
        self.next_task_id = 1
        self.load_data()

    def save_data(self):
        data = {
            'tasks': [task.to_dict() for task in self.tasks],
            'users': [user.to_dict() for user in self.users],
            'assignments': [assignment.to_dict() for assignment in self.assignments],
            'next_task_id': self.next_task_id
        }
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=2)

    def load_data(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                
                # Cargar usuarios
                self.users = [Usuario.from_dict(user_data) for user_data in data.get('users', [])]
                
                # Cargar tareas
                self.tasks = [Tarea.from_dict(task_data) for task_data in data.get('tasks', [])]
                
                # Cargar asignaciones
                self.assignments = [Asignacion.from_dict(assign_data) for assign_data in data.get('assignments', [])]
                
                # Cargar next_task_id
                self.next_task_id = data.get('next_task_id', 1)
                
        except FileNotFoundError:
            self.tasks = []
            self.users = []
            self.assignments = []
            self.next_task_id = 1

    def get_user_by_alias(self, alias):
        """Obtiene un usuario por su alias"""
        for user in self.users:
            if user.alias == alias:
                return user
        return None

    def get_task_by_id(self, task_id):
        """Obtiene una tarea por su ID"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def create_user(self, alias, nombre):
        """Crea un nuevo usuario"""
        if self.get_user_by_alias(alias):
            raise ValueError(f"Usuario con alias '{alias}' ya existe")
        
        user = Usuario(alias, nombre)
        self.users.append(user)
        self.save_data()
        return user

    def create_task(self, nombre, descripcion, usuario_alias, rol):
        """Crea una nueva tarea"""
        user = self.get_user_by_alias(usuario_alias)
        if not user:
            raise ValueError(f"Usuario '{usuario_alias}' no existe")
        
        task = Tarea(self.next_task_id, nombre, descripcion, usuario_alias, rol)
        self.tasks.append(task)
        
        # Actualizar lista de tareas del usuario
        user.tareas_asignadas.append(self.next_task_id)
        
        self.next_task_id += 1
        self.save_data()
        return task

    def update_task_state(self, task_id, nuevo_estado):
        """Actualiza el estado de una tarea"""
        task = self.get_task_by_id(task_id)
        if not task:
            raise ValueError(f"Tarea con ID {task_id} no existe")
        
        # Verificar si puede finalizar (si el nuevo estado es finalizada)
        if nuevo_estado == 'finalizada' and not task.puede_finalizar(self.tasks):
            raise ValueError("No se puede finalizar la tarea porque tiene dependencias sin finalizar")
        
        task.cambiar_estado(nuevo_estado)
        self.save_data()
        return task

    def assign_user_to_task(self, task_id, usuario_alias, rol):
        """Asigna un usuario a una tarea"""
        task = self.get_task_by_id(task_id)
        if not task:
            raise ValueError(f"Tarea con ID {task_id} no existe")
        
        user = self.get_user_by_alias(usuario_alias)
        if not user:
            raise ValueError(f"Usuario '{usuario_alias}' no existe")
        
        task.asignar_usuario(usuario_alias, rol)
        
        # Actualizar lista de tareas del usuario
        if task_id not in user.tareas_asignadas:
            user.tareas_asignadas.append(task_id)
        
        self.save_data()
        return task

    def remove_user_from_task(self, task_id, usuario_alias):
        """Remueve un usuario de una tarea"""
        task = self.get_task_by_id(task_id)
        if not task:
            raise ValueError(f"Tarea con ID {task_id} no existe")
        
        user = self.get_user_by_alias(usuario_alias)
        if not user:
            raise ValueError(f"Usuario '{usuario_alias}' no existe")
        
        task.remover_usuario(usuario_alias)
        
        # Actualizar lista de tareas del usuario
        if task_id in user.tareas_asignadas:
            user.tareas_asignadas.remove(task_id)
        
        self.save_data()
        return task

    def add_task_dependency(self, task_id, dependency_task_id):
        """Agrega una dependencia a una tarea"""
        task = self.get_task_by_id(task_id)
        if not task:
            raise ValueError(f"Tarea con ID {task_id} no existe")
        
        dependency_task = self.get_task_by_id(dependency_task_id)
        if not dependency_task:
            raise ValueError(f"Tarea de dependencia con ID {dependency_task_id} no existe")
        
        task.agregar_dependencia(dependency_task_id)
        self.save_data()
        return task

    def remove_task_dependency(self, task_id, dependency_task_id):
        """Remueve una dependencia de una tarea"""
        task = self.get_task_by_id(task_id)
        if not task:
            raise ValueError(f"Tarea con ID {task_id} no existe")
        
        task.remover_dependencia(dependency_task_id)
        self.save_data()
        return task

    def get_user_with_tasks(self, alias):
        """Obtiene un usuario con todas sus tareas asignadas"""
        user = self.get_user_by_alias(alias)
        if not user:
            return None
        
        user_tasks = []
        for task_id in user.tareas_asignadas:
            task = self.get_task_by_id(task_id)
            if task:
                user_tasks.append(task.to_dict())
        
        return {
            "alias": user.alias,
            "nombre": user.nombre,
            "tareas": user_tasks
        }