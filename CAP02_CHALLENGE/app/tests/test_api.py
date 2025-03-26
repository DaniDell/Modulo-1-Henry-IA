import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_task():
    response = client.post("/tasks/", json={"title": "Test Task", "description": "This is a test task", "completed": False})
    assert response.status_code == 200
    assert response.json()["title"] == "Test Task"

def test_get_task():
    # Primero, creamos una tarea
    response = client.post("/tasks/", json={"title": "Test Task", "description": "This is a test task", "completed": False})
    task_id = response.json()["id"]
    
    # Luego, intentamos obtener la tarea creada
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["id"] == task_id

def test_get_all_tasks():
    response = client.get("/tasks/")
    assert response.status_code == 200
    assert isinstance(response.json()["tasks"], list)

def test_update_task():
    # Primero, creamos una tarea
    response = client.post("/tasks/", json={"title": "Test Task", "description": "This is a test task", "completed": False})
    task_id = response.json()["id"]
    
    # Luego, intentamos actualizar la tarea creada
    response = client.put(f"/tasks/{task_id}", json={"title": "Updated Task", "description": "This task has been updated", "completed": True})
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Task"

def test_delete_task():
    # Primero, creamos una tarea
    response = client.post("/tasks/", json={"title": "Test Task", "description": "This is a test task", "completed": False})
    task_id = response.json()["id"]
    
    # Luego, intentamos eliminar la tarea creada
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Task deleted successfully"

def test_delete_all_tasks():
    # Primero, creamos algunas tareas
    client.post("/tasks/", json={"title": "Test Task 1", "description": "This is a test task", "completed": False})
    client.post("/tasks/", json={"title": "Test Task 2", "description": "This is another test task", "completed": False})
    
    # Luego, intentamos eliminar todas las tareas
    response = client.delete("/tasks/")
    assert response.status_code == 200
    assert response.json()["message"] == "Todas las tareas han sido eliminadas exitosamente"