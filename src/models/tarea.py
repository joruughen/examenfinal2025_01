class Tarea:
    ESTADOS_VALIDOS = ['nueva', 'en_progreso', 'finalizada']
    TRANSICIONES_VALIDAS = {
        'nueva': ['en_progreso'],
        'en_progreso': ['nueva', 'finalizada'],
        'finalizada': []
    }
    ROLES_VALIDOS = ['programador', 'pruebas', 'infra']
    
    def __init__(self, id, nombre, descripcion, usuario_creador, rol):
        # Validar rol al crear la tarea
        if rol not in self.ROLES_VALIDOS:
            raise ValueError(f"Rol '{rol}' no es válido")
            
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.usuario_creador = usuario_creador
        self.rol = rol
        self.estado = 'nueva'
        self.dependencias = []  # Lista de IDs de tareas de las que depende
        self.usuarios_asignados = []  # Lista de diccionarios {'usuario': alias, 'rol': rol}
        
        # Asignar automáticamente al usuario creador
        self.usuarios_asignados.append({'usuario': usuario_creador, 'rol': rol})
    
    def cambiar_estado(self, nuevo_estado):
        """Cambia el estado de la tarea si la transición es válida"""
        if nuevo_estado not in self.ESTADOS_VALIDOS:
            raise ValueError(f"Estado '{nuevo_estado}' no es válido")
        
        if nuevo_estado not in self.TRANSICIONES_VALIDAS[self.estado]:
            raise ValueError(f"No se puede cambiar de '{self.estado}' a '{nuevo_estado}'")
        
        self.estado = nuevo_estado
    
    def asignar_usuario(self, usuario_alias, rol):
        """Asigna un usuario a la tarea con un rol específico"""
        if rol not in self.ROLES_VALIDOS:
            raise ValueError(f"Rol '{rol}' no es válido")
        
        # Verificar si el usuario ya está asignado
        for asignacion in self.usuarios_asignados:
            if asignacion['usuario'] == usuario_alias:
                raise ValueError(f"Usuario '{usuario_alias}' ya está asignado a esta tarea")
        
        self.usuarios_asignados.append({'usuario': usuario_alias, 'rol': rol})
    
    def remover_usuario(self, usuario_alias):
        """Remueve un usuario de la tarea"""
        # Verificar que el usuario esté asignado
        usuario_encontrado = False
        for i, asignacion in enumerate(self.usuarios_asignados):
            if asignacion['usuario'] == usuario_alias:
                usuario_encontrado = True
                asignacion_index = i
                break
        
        if not usuario_encontrado:
            raise ValueError(f"Usuario '{usuario_alias}' no está asignado a esta tarea")
        
        # Verificar que no sea el último usuario (siempre debe haber al menos uno)
        if len(self.usuarios_asignados) <= 1:
            raise ValueError("Una tarea debe tener al menos un usuario asignado")
        
        self.usuarios_asignados.pop(asignacion_index)
    
    def agregar_dependencia(self, tarea_id):
        """Agrega una dependencia a la tarea"""
        if tarea_id in self.dependencias:
            raise ValueError(f"La tarea {tarea_id} ya es una dependencia")
        
        self.dependencias.append(tarea_id)
    
    def remover_dependencia(self, tarea_id):
        """Remueve una dependencia de la tarea"""
        if tarea_id not in self.dependencias:
            raise ValueError(f"La tarea {tarea_id} no es una dependencia")
        
        self.dependencias.remove(tarea_id)
    
    def puede_finalizar(self, todas_las_tareas):
        """Verifica si la tarea puede ser finalizada (todas sus dependencias están finalizadas)"""
        for dep_id in self.dependencias:
            tarea_dep = None
            for tarea in todas_las_tareas:
                if tarea.id == dep_id:
                    tarea_dep = tarea
                    break
            
            if tarea_dep is None or tarea_dep.estado != 'finalizada':
                return False
        
        return True
    
    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "usuario_creador": self.usuario_creador,
            "rol": self.rol,
            "estado": self.estado,
            "dependencias": self.dependencias,
            "usuarios_asignados": self.usuarios_asignados
        }
    
    @classmethod
    def from_dict(cls, data):
        tarea = cls(
            data["id"],
            data["nombre"],
            data["descripcion"],
            data["usuario_creador"],
            data["rol"]
        )
        tarea.estado = data.get("estado", "nueva")
        tarea.dependencias = data.get("dependencias", [])
        # Esta línea debe ejecutarse para cubrir la línea 66
        usuarios_asignados_data = data.get("usuarios_asignados", [])
        tarea.usuarios_asignados = usuarios_asignados_data
        return tarea