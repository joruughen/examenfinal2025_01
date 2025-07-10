from flask import Flask, jsonify, request
from data_handler import DataHandler
import re

app = Flask(__name__)
data_handler = DataHandler()

class TaskController:
    def __init__(self, data_handler):
        self.data_handler = data_handler

# Instanciar el controlador
task_controller = TaskController(data_handler)

@app.route('/usuarios/mialias=<alias>', methods=['GET'])
def get_user_with_tasks(alias):
    """
    GET /usuarios/mialias=XXXX
    Retorna datos de usuario y sus tareas asignadas
    """
    try:
        user_data = data_handler.get_user_with_tasks(alias)
        if not user_data:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        return jsonify(user_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/usuarios', methods=['POST'])
def create_user():
    """
    POST /usuarios
    Body: {"contacto": "{alias del contacto}", "nombre": "nombre del usuario"}
    Crea un nuevo usuario
    """
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        if not data or 'contacto' not in data or 'nombre' not in data:
            return jsonify({"error": "Campos 'contacto' y 'nombre' son requeridos"}), 400
        
        contacto = data['contacto']
        nombre = data['nombre']
        
        # Validar que no estén vacíos
        if not contacto or not nombre:
            return jsonify({"error": "Los campos 'contacto' y 'nombre' no pueden estar vacíos"}), 400
        
        # Crear usuario
        user = data_handler.create_user(contacto, nombre)
        
        return jsonify({
            "message": "Usuario creado exitosamente",
            "usuario": user.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 422
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tasks', methods=['POST'])
def create_task():
    """
    POST /tasks
    Body: {"nombre": "nombre de la tarea", "descripcion": "descripción de la tarea", 
           "usuario": "alias", "rol": "rol: programador o pruebas o infra"}
    Retorna el id de la tarea creada
    """
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        required_fields = ['nombre', 'descripcion', 'usuario', 'rol']
        for field in required_fields:
            if not data or field not in data:
                return jsonify({"error": f"Campo '{field}' es requerido"}), 400
        
        nombre = data['nombre']
        descripcion = data['descripcion']
        usuario = data['usuario']
        rol = data['rol']
        
        # Validar que no estén vacíos
        if not nombre or not descripcion or not usuario or not rol:
            return jsonify({"error": "Todos los campos son requeridos y no pueden estar vacíos"}), 400
        
        # Validar rol
        if rol not in ['programador', 'pruebas', 'infra']:
            return jsonify({"error": "Rol debe ser 'programador', 'pruebas' o 'infra'"}), 422
        
        # Crear tarea
        task = data_handler.create_task(nombre, descripcion, usuario, rol)
        
        return jsonify({
            "message": "Tarea creada exitosamente",
            "task_id": task.id
        }), 201
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 422
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tasks/<int:task_id>', methods=['POST'])
def update_task_status(task_id):
    """
    POST /tasks/{id}
    Body: {"estado": "nuevoestado"}
    Actualiza el estado de una tarea
    """
    try:
        data = request.get_json()
        
        # Validar campo requerido
        if not data or 'estado' not in data:
            return jsonify({"error": "Campo 'estado' es requerido"}), 400
        
        nuevo_estado = data['estado']
        
        # Validar que no esté vacío
        if not nuevo_estado:
            return jsonify({"error": "El campo 'estado' no puede estar vacío"}), 400
        
        # Validar estado
        if nuevo_estado not in ['nueva', 'en_progreso', 'finalizada']:
            return jsonify({"error": "Estado debe ser 'nueva', 'en_progreso' o 'finalizada'"}), 422
        
        # Actualizar tarea
        task = data_handler.update_task_state(task_id, nuevo_estado)
        
        return jsonify({
            "message": "Estado de tarea actualizado exitosamente",
            "task": task.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 422
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tasks/<int:task_id>/users', methods=['POST'])
def manage_task_users(task_id):
    """
    POST /tasks/{id}/users
    Body: {"usuario": "alias", "rol": "rol: programador o pruebas o infra", "accion": "adicionar/remover"}
    Asigna o remueve usuarios de una tarea
    """
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        required_fields = ['usuario', 'accion']
        for field in required_fields:
            if not data or field not in data:
                return jsonify({"error": f"Campo '{field}' es requerido"}), 400
        
        usuario = data['usuario']
        accion = data['accion']
        
        # Validar que no estén vacíos
        if not usuario or not accion:
            return jsonify({"error": "Los campos 'usuario' y 'accion' no pueden estar vacíos"}), 400
        
        # Validar acción
        if accion not in ['adicionar', 'remover']:
            return jsonify({"error": "Acción debe ser 'adicionar' o 'remover'"}), 422
        
        if accion == 'adicionar':
            # Validar rol para adicionar
            if 'rol' not in data:
                return jsonify({"error": "Campo 'rol' es requerido para adicionar usuario"}), 400
            
            rol = data['rol']
            if not rol:
                return jsonify({"error": "El campo 'rol' no puede estar vacío"}), 400
            
            if rol not in ['programador', 'pruebas', 'infra']:
                return jsonify({"error": "Rol debe ser 'programador', 'pruebas' o 'infra'"}), 422
            
            task = data_handler.assign_user_to_task(task_id, usuario, rol)
            message = "Usuario asignado exitosamente"
        else:
            task = data_handler.remove_user_from_task(task_id, usuario)
            message = "Usuario removido exitosamente"
        
        return jsonify({
            "message": message,
            "task": task.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 422
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tasks/<int:task_id>/dependencies', methods=['POST'])
def manage_task_dependencies(task_id):
    """
    POST /tasks/{id}/dependencies
    Body: {"dependencytaskid": "id de la tarea de la que se va a depender", "accion": "adicionar/remover"}
    Agrega o remueve dependencias de una tarea
    """
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        required_fields = ['dependencytaskid', 'accion']
        for field in required_fields:
            if not data or field not in data:
                return jsonify({"error": f"Campo '{field}' es requerido"}), 400
        
        dependency_task_id = data['dependencytaskid']
        accion = data['accion']
        
        # Validar que no estén vacíos
        if dependency_task_id is None or not accion:
            return jsonify({"error": "Los campos 'dependencytaskid' y 'accion' no pueden estar vacíos"}), 400
        
        # Validar acción
        if accion not in ['adicionar', 'remover']:
            return jsonify({"error": "Acción debe ser 'adicionar' o 'remover'"}), 422
        
        # Validar que dependency_task_id sea un entero
        try:
            dependency_task_id = int(dependency_task_id)
        except (ValueError, TypeError):
            return jsonify({"error": "dependencytaskid debe ser un número"}), 422
        
        # Validar que no sea la misma tarea
        if dependency_task_id == task_id:
            return jsonify({"error": "Una tarea no puede depender de sí misma"}), 422
        
        if accion == 'adicionar':
            task = data_handler.add_task_dependency(task_id, dependency_task_id)
            message = "Dependencia agregada exitosamente"
        else:
            task = data_handler.remove_task_dependency(task_id, dependency_task_id)
            message = "Dependencia removida exitosamente"
        
        return jsonify({
            "message": message,
            "task": task.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 422
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Manejadores de errores
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Recurso no encontrado"}), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Solicitud inválida"}), 400

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"error": "Error interno del servidor"}), 500

# Endpoint dummy original (mantener para compatibilidad)
@app.route('/dummy', methods=['GET'])
def dummy_endpoint():
    return jsonify({"message": "This is a dummy endpoint!"})

# Endpoint adicional para listar todos los usuarios (útil para debugging)
@app.route('/usuarios', methods=['GET'])
def list_users():
    """GET /usuarios - Lista todos los usuarios"""
    try:
        users_data = []
        for user in data_handler.users:
            users_data.append(user.to_dict())
        return jsonify({"usuarios": users_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint adicional para listar todas las tareas (útil para debugging)
@app.route('/tasks', methods=['GET'])
def list_tasks():
    """GET /tasks - Lista todas las tareas"""
    try:
        tasks_data = []
        for task in data_handler.tasks:
            tasks_data.append(task.to_dict())
        return jsonify({"tareas": tasks_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)