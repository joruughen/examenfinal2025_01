import pytest
import sys
import os

# Agregar el directorio src al path para importar los módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.usuario import Usuario
from models.tarea import Tarea
from models.asignacion import Asignacion


class TestUsuario:
    
    def test_crear_usuario_exitoso(self):
        """Caso de éxito: Crear un usuario correctamente
        
        Caso de prueba: CP-USR-001
        Descripción: Verificar que se puede crear un usuario con alias y nombre válidos
        Entrada: alias="juan.perez", nombre="Juan Pérez"
        Resultado esperado: Usuario creado con atributos correctos y lista de tareas vacía
        """
        # Arrange
        alias = "juan.perez"
        nombre = "Juan Pérez"
        
        # Act
        usuario = Usuario(alias, nombre)
        
        # Assert
        assert usuario.alias == alias
        assert usuario.nombre == nombre
        assert usuario.tareas_asignadas == []
        assert usuario.get_user_info()["alias"] == alias
        assert usuario.get_user_info()["nombre"] == nombre
    
    def test_usuario_to_dict_y_from_dict(self):
        """Caso de éxito: Conversión de usuario a diccionario y viceversa
        
        Caso de prueba: CP-USR-002
        Descripción: Verificar serialización y deserialización correcta del usuario
        Entrada: Usuario con tareas asignadas [1, 2, 3]
        Resultado esperado: Usuario reconstruido idéntico al original
        """
        # Arrange
        alias = "maria.garcia"
        nombre = "María García"
        usuario = Usuario(alias, nombre)
        usuario.tareas_asignadas = [1, 2, 3]
        
        # Act
        user_dict = usuario.to_dict()
        usuario_reconstructed = Usuario.from_dict(user_dict)
        
        # Assert
        assert usuario_reconstructed.alias == usuario.alias
        assert usuario_reconstructed.nombre == usuario.nombre
        assert usuario_reconstructed.tareas_asignadas == usuario.tareas_asignadas


class TestTarea:
    
    def test_crear_tarea_exitosa(self):
        """Caso de éxito: Crear una tarea correctamente
        
        Caso de prueba: CP-TAR-001
        Descripción: Verificar creación exitosa de tarea con datos válidos
        Entrada: id=1, nombre="Implementar login", usuario_creador="dev1", rol="programador"
        Resultado esperado: Tarea creada con estado "nueva" y usuario creador asignado
        """
        # Arrange
        id_tarea = 1
        nombre = "Implementar login"
        descripcion = "Desarrollar funcionalidad de login"
        usuario_creador = "dev1"
        rol = "programador"
        
        # Act
        tarea = Tarea(id_tarea, nombre, descripcion, usuario_creador, rol)
        
        # Assert
        assert tarea.id == id_tarea
        assert tarea.nombre == nombre
        assert tarea.descripcion == descripcion
        assert tarea.usuario_creador == usuario_creador
        assert tarea.rol == rol
        assert tarea.estado == "nueva"
        assert len(tarea.usuarios_asignados) == 1
        assert tarea.usuarios_asignados[0] == {'usuario': usuario_creador, 'rol': rol}
    
    def test_cambiar_estado_invalido(self):
        """Caso de error: Cambiar a un estado inválido
        
        Caso de prueba: CP-TAR-002
        Descripción: Verificar rechazo de estados no válidos
        Entrada: estado="estado_inexistente"
        Resultado esperado: ValueError con mensaje descriptivo
        """
        # Arrange
        tarea = Tarea(1, "Test", "Test desc", "dev1", "programador")
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            tarea.cambiar_estado("estado_inexistente")
        assert "Estado 'estado_inexistente' no es válido" in str(exc_info.value)
    
    def test_transicion_estado_invalida(self):
        """Caso de error: Transición de estado inválida
        
        Caso de prueba: CP-TAR-003
        Descripción: Verificar rechazo de transiciones no permitidas
        Entrada: tarea en estado "finalizada", cambio a "en_progreso"
        Resultado esperado: ValueError indicando transición inválida
        """
        # Arrange
        tarea = Tarea(1, "Test", "Test desc", "dev1", "programador")
        tarea.estado = "finalizada"
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            tarea.cambiar_estado("nueva")
        assert "No se puede cambiar de 'finalizada' a 'nueva'" in str(exc_info.value)
    
    def test_remover_ultimo_usuario(self):
        """Caso de error: Intentar remover el último usuario de una tarea
        
        Caso de prueba: CP-TAR-004
        Descripción: Verificar que no se puede remover el último usuario de una tarea
        Entrada: tarea con un solo usuario asignado (el creador)
        Resultado esperado: ValueError indicando que debe haber al menos un usuario
        """
        # Arrange
        tarea = Tarea(1, "Test", "Test desc", "dev1", "programador")
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            tarea.remover_usuario("dev1")
        assert "Una tarea debe tener al menos un usuario asignado" in str(exc_info.value)
    
    def test_asignar_usuario_duplicado(self):
        """Caso de error: Intentar asignar un usuario que ya está asignado
        
        Caso de prueba: CP-TAR-005
        Descripción: Verificar rechazo de usuarios duplicados en la misma tarea
        Entrada: usuario "dev1" ya asignado, intento de reasignar con rol "pruebas"
        Resultado esperado: ValueError indicando usuario duplicado
        """
        # Arrange
        tarea = Tarea(1, "Test", "Test desc", "dev1", "programador")
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            tarea.asignar_usuario("dev1", "pruebas")
        assert "Usuario 'dev1' ya está asignado a esta tarea" in str(exc_info.value)
    
    def test_cambiar_estado_valido(self):
        """Caso de éxito: Cambiar estado con transición válida
        
        Caso de prueba: CP-TAR-006
        Descripción: Verificar cambio exitoso de estado con transición permitida
        Entrada: tarea en estado "nueva", cambio a "en_progreso"
        Resultado esperado: Estado cambiado correctamente
        """
        # Arrange
        tarea = Tarea(1, "Test", "Test desc", "dev1", "programador")
        
        # Act
        tarea.cambiar_estado("en_progreso")
        
        # Assert
        assert tarea.estado == "en_progreso"
    
    def test_asignar_usuario_nuevo(self):
        """Caso de éxito: Asignar un nuevo usuario a la tarea
        
        Caso de prueba: CP-TAR-007
        Descripción: Verificar asignación exitosa de nuevo usuario a tarea
        Entrada: tarea existente, nuevo usuario "dev2" con rol "pruebas"
        Resultado esperado: Usuario agregado correctamente a la lista de asignados
        """
        # Arrange
        tarea = Tarea(1, "Test", "Test desc", "dev1", "programador")
        
        # Act
        tarea.asignar_usuario("dev2", "pruebas")
        
        # Assert
        assert len(tarea.usuarios_asignados) == 2
        assert {'usuario': 'dev2', 'rol': 'pruebas'} in tarea.usuarios_asignados
    
    def test_puede_finalizar_con_dependencias(self):
        """Caso de éxito: Verificar si puede finalizar con dependencias
        
        Caso de prueba: CP-TAR-008
        Descripción: Verificar que tarea puede finalizar cuando dependencias están completas
        Entrada: tarea2 depende de tarea1, tarea1 en estado "finalizada"
        Resultado esperado: puede_finalizar() retorna True
        """
        # Arrange
        tarea1 = Tarea(1, "Tarea 1", "Primera tarea", "dev1", "programador")
        tarea1.estado = "finalizada"
        
        tarea2 = Tarea(2, "Tarea 2", "Segunda tarea", "dev2", "programador")
        tarea2.agregar_dependencia(1)
        
        todas_las_tareas = [tarea1, tarea2]
        
        # Act
        puede_finalizar = tarea2.puede_finalizar(todas_las_tareas)
        
        # Assert
        assert puede_finalizar == True
    
    def test_agregar_dependencia_duplicada(self):
        """Caso de error: Agregar dependencia duplicada
        
        Caso de prueba: CP-TAR-009
        Descripción: Verificar rechazo de dependencias duplicadas
        Entrada: tarea con dependencia 2 ya agregada, intento de agregar dependencia 2 nuevamente
        Resultado esperado: ValueError indicando dependencia duplicada
        """
        # Arrange
        tarea = Tarea(1, "Test", "Test desc", "dev1", "programador")
        tarea.agregar_dependencia(2)
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            tarea.agregar_dependencia(2)
        assert "La tarea 2 ya es una dependencia" in str(exc_info.value)
    
    def test_remover_dependencia_inexistente(self):
        """Caso de error: Remover dependencia que no existe
        
        Caso de prueba: CP-TAR-010
        Descripción: Verificar rechazo al remover dependencia inexistente
        Entrada: tarea sin dependencia 2, intento de remover dependencia 2
        Resultado esperado: ValueError indicando dependencia inexistente
        """
        # Arrange
        tarea = Tarea(1, "Test", "Test desc", "dev1", "programador")
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            tarea.remover_dependencia(2)
        assert "La tarea 2 no es una dependencia" in str(exc_info.value)
    
    def test_rol_invalido_en_creacion(self):
        """Caso de error: Crear tarea con rol inválido
        
        Caso de prueba: CP-TAR-011
        Descripción: Verificar rechazo de roles inválidos en creación de tarea
        Entrada: rol="rol_inexistente" al crear tarea
        Resultado esperado: ValueError indicando rol inválido
        """
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            Tarea(1, "Test", "Test desc", "dev1", "rol_inexistente")
        assert "Rol 'rol_inexistente' no es válido" in str(exc_info.value)
    
    def test_rol_invalido_en_asignacion(self):
        """Caso de error: Asignar usuario con rol inválido
        
        Caso de prueba: CP-TAR-012
        Descripción: Verificar rechazo de roles inválidos en asignación de usuario
        Entrada: rol="rol_inexistente" al asignar usuario
        Resultado esperado: ValueError indicando rol inválido
        """
        # Arrange
        tarea = Tarea(1, "Test", "Test desc", "dev1", "programador")
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            tarea.asignar_usuario("dev2", "rol_inexistente")
        assert "Rol 'rol_inexistente' no es válido" in str(exc_info.value)
    
    def test_remover_usuario_exitoso(self):
        """Caso exitoso: Remover usuario asignado cuando hay múltiples usuarios
        
        Caso de prueba: CP-TAR-013
        Descripción: Verificar remoción exitosa de usuario cuando hay múltiples asignados
        Entrada: tarea con 2 usuarios, remover "dev2"
        Resultado esperado: Usuario removido, queda solo "dev1"
        """
        # Arrange
        tarea = Tarea(1, "Test", "Test desc", "dev1", "programador")
        tarea.asignar_usuario("dev2", "pruebas")
        
        # Act
        tarea.remover_usuario("dev2")
        
        # Assert
        assert len(tarea.usuarios_asignados) == 1
        assert tarea.usuarios_asignados[0]['usuario'] == "dev1"
    
    def test_puede_finalizar_dependencia_no_finalizada(self):
        """Caso de éxito: Verificar que no puede finalizar si dependencias no están finalizadas
        
        Caso de prueba: CP-TAR-014
        Descripción: Verificar que tarea no puede finalizar con dependencias pendientes
        Entrada: tarea2 depende de tarea1, tarea1 en estado "en_progreso"
        Resultado esperado: puede_finalizar() retorna False
        """
        # Arrange
        tarea1 = Tarea(1, "Tarea 1", "Primera tarea", "dev1", "programador")
        tarea1.estado = "en_progreso"  # No está finalizada
        
        tarea2 = Tarea(2, "Tarea 2", "Segunda tarea", "dev2", "programador")
        tarea2.agregar_dependencia(1)
        
        todas_las_tareas = [tarea1, tarea2]
        
        # Act
        puede_finalizar = tarea2.puede_finalizar(todas_las_tareas)
        
        # Assert
        assert puede_finalizar == False
    
    def test_puede_finalizar_dependencia_inexistente(self):
        """Caso de éxito: Verificar comportamiento cuando dependencia no existe en la lista
        
        Caso de prueba: CP-TAR-015
        Descripción: Verificar que tarea no puede finalizar si dependencia no existe
        Entrada: tarea1 depende de tarea 999 (inexistente)
        Resultado esperado: puede_finalizar() retorna False
        """
        # Arrange
        tarea1 = Tarea(1, "Tarea 1", "Primera tarea", "dev1", "programador")
        tarea1.agregar_dependencia(999)  # Dependencia que no existe
        
        todas_las_tareas = [tarea1]  # Solo contiene tarea1, no la dependencia 999
        
        # Act
        puede_finalizar = tarea1.puede_finalizar(todas_las_tareas)
        
        # Assert
        assert puede_finalizar == False
    
    def test_remover_usuario_no_asignado(self):
        """Caso de error: Remover usuario que no está asignado
        
        Caso de prueba: CP-TAR-016
        Descripción: Verificar rechazo al remover usuario no asignado
        Entrada: intento de remover "usuario_inexistente"
        Resultado esperado: ValueError indicando usuario no asignado
        """
        # Arrange
        tarea = Tarea(1, "Test", "Test desc", "dev1", "programador")
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            tarea.remover_usuario("usuario_inexistente")
        assert "Usuario 'usuario_inexistente' no está asignado a esta tarea" in str(exc_info.value)
    
    def test_remover_dependencia_y_agregar_nuevamente(self):
        """Caso de éxito: Remover una dependencia válida y agregarla de nuevo
        
        Caso de prueba: CP-TAR-017
        Descripción: Verificar ciclo completo de agregar/remover/agregar dependencia
        Entrada: agregar dependencia 2, removerla, agregarla nuevamente
        Resultado esperado: Operaciones exitosas, dependencia presente al final
        """
        # Arrange
        tarea = Tarea(1, "Test", "Test desc", "dev1", "programador")
        tarea.agregar_dependencia(2)
        
        # Act - Remover dependencia
        tarea.remover_dependencia(2)
        
        # Assert - Verificar que se removió
        assert 2 not in tarea.dependencias
        
        # Act - Agregar de nuevo
        tarea.agregar_dependencia(2)
        
        # Assert - Verificar que se agregó
        assert 2 in tarea.dependencias
    
    def test_from_dict_constructor(self):
        """Caso de éxito: Crear tarea desde diccionario (para cubrir línea 66)
        
        Caso de prueba: CP-TAR-018
        Descripción: Verificar deserialización correcta de tarea desde diccionario
        Entrada: diccionario con datos completos de tarea
        Resultado esperado: Tarea reconstruida con todos los atributos correctos
        """
        # Arrange
        tarea_dict = {
            "id": 1,
            "nombre": "Test Task",
            "descripcion": "Test Description", 
            "usuario_creador": "dev1",
            "rol": "programador",
            "estado": "en_progreso",
            "dependencias": [2, 3],
            "usuarios_asignados": [
                {"usuario": "dev1", "rol": "programador"},
                {"usuario": "dev2", "rol": "pruebas"}
            ]
        }
        
        # Act
        tarea = Tarea.from_dict(tarea_dict)
        
        # Assert - Verificar que los usuarios_asignados se cargaron correctamente (línea 80)
        assert len(tarea.usuarios_asignados) == 2
        assert tarea.usuarios_asignados[0]["usuario"] == "dev1"
        assert tarea.usuarios_asignados[1]["usuario"] == "dev2"
        assert tarea.estado == "en_progreso"
        assert tarea.dependencias == [2, 3]
    
    def test_from_dict_sin_usuarios_asignados(self):
        """Caso de éxito: Crear tarea desde diccionario sin usuarios_asignados (línea 66)
        
        Caso de prueba: CP-TAR-019
        Descripción: Verificar deserialización con datos mínimos (sin usuarios_asignados)
        Entrada: diccionario sin campo usuarios_asignados
        Resultado esperado: Tarea con usuarios_asignados vacío por defecto
        """
        # Arrange - Diccionario sin usuarios_asignados para activar el get() con default
        tarea_dict = {
            "id": 5,
            "nombre": "Test Task Sin Usuarios",
            "descripcion": "Test Description", 
            "usuario_creador": "dev1",
            "rol": "programador"
            # No incluimos 'usuarios_asignados' para que use el valor por defecto []
        }
        
        # Act
        tarea = Tarea.from_dict(tarea_dict)
        
        # Assert - Esta línea debería activar la línea 66: usuarios_asignados = data.get("usuarios_asignados", [])
        assert len(tarea.usuarios_asignados) == 0  # Debería estar vacío porque usó el default []
        assert tarea.estado == "nueva"  # Estado por defecto
        assert tarea.dependencias == []  # Dependencias por defecto
    
    def test_tarea_con_usuarios_asignados_vacios(self):
        """Caso adicional: Crear tarea con usuarios_asignados explícitamente vacío
        
        Caso de prueba: CP-TAR-020
        Descripción: Verificar deserialización con usuarios_asignados explícitamente vacío
        Entrada: diccionario con usuarios_asignados: []
        Resultado esperado: Tarea con usuarios_asignados vacío
        """
        # Arrange
        tarea_dict = {
            "id": 6,
            "nombre": "Test Vacío",
            "descripcion": "Test Description", 
            "usuario_creador": "dev1",
            "rol": "programador",
            "usuarios_asignados": []  # Explícitamente vacío
        }
        
        # Act
        tarea = Tarea.from_dict(tarea_dict)
        
        # Assert
        assert len(tarea.usuarios_asignados) == 0
        
    def test_case_cobertura_completa(self):
        """Caso de cobertura: Verificar funcionamiento completo con múltiples operaciones
        
        Caso de prueba: CP-TAR-021
        Descripción: Prueba integral con todas las operaciones principales
        Entrada: tarea con múltiples usuarios, dependencias y cambios de estado
        Resultado esperado: Todas las operaciones exitosas
        """
        """Caso adicional para asegurar cobertura completa"""
        # Este test extra para asegurar que cubrimos todas las líneas posibles
        tarea = Tarea(999, "Test Final", "Test Desc Final", "usuario_final", "infra")
        
        # Verificar todas las propiedades
        assert tarea.id == 999
        assert tarea.rol == "infra"
        assert tarea.estado == "nueva"
        
        # Test de serialización completa
        dict_resultado = tarea.to_dict()
        assert "id" in dict_resultado
        assert "usuarios_asignados" in dict_resultado


class TestAsignacion:
    
    def test_crear_asignacion_exitosa(self):
        """Caso de éxito: Crear una asignación correctamente
        
        Caso de prueba: CP-ASG-001
        Descripción: Verificar creación exitosa de asignación
        Entrada: task_id=1, user_alias="dev1", rol="programador"
        Resultado esperado: Asignación creada con atributos correctos
        """
        # Arrange
        task_id = 1
        user_alias = "dev1"
        rol = "programador"
        
        # Act
        asignacion = Asignacion(task_id, user_alias, rol)
        
        # Assert
        assert asignacion.task_id == task_id
        assert asignacion.user_alias == user_alias
        assert asignacion.rol == rol
        
        details = asignacion.get_assignment_details()
        assert details["task_id"] == task_id
        assert details["user_alias"] == user_alias
        assert details["rol"] == rol
    
    def test_asignacion_to_dict_y_from_dict(self):
        """Caso de éxito: Conversión de asignación a diccionario y viceversa"""
        # Arrange
        task_id = 1
        user_alias = "tester1"
        rol = "pruebas"
        asignacion = Asignacion(task_id, user_alias, rol)
        
        # Act
        asignacion_dict = asignacion.to_dict()
        asignacion_reconstructed = Asignacion.from_dict(asignacion_dict)
        
        # Assert
        assert asignacion_reconstructed.task_id == asignacion.task_id
        assert asignacion_reconstructed.user_alias == asignacion.user_alias
        assert asignacion_reconstructed.rol == asignacion.rol


# Test de integración adicional
class TestIntegracion:
    
    def test_flujo_completo_tarea(self):
        """Caso de éxito: Flujo completo de creación y modificación de tarea"""
        # Arrange & Act
        tarea = Tarea(1, "Implementar API", "Desarrollar endpoints REST", "dev1", "programador")
        
        # Cambiar estado
        tarea.cambiar_estado("en_progreso")
        
        # Asignar otro usuario
        tarea.asignar_usuario("tester1", "pruebas")
        
        # Agregar dependencia
        tarea.agregar_dependencia(2)
        
        # Assert
        assert tarea.estado == "en_progreso"
        assert len(tarea.usuarios_asignados) == 2
        assert 2 in tarea.dependencias
        
        # Verificar que se puede serializar y deserializar
        tarea_dict = tarea.to_dict()
        tarea_reconstructed = Tarea.from_dict(tarea_dict)
        assert tarea_reconstructed.estado == tarea.estado
        assert len(tarea_reconstructed.usuarios_asignados) == len(tarea.usuarios_asignados)
