# Guía para Realizar Pruebas en la API de Gestión de Tareas

Para asegurarte de que todas las operaciones de tu API funcionan correctamente, puedes implementar pruebas utilizando un marco de pruebas como `pytest` junto con `httpx` para realizar solicitudes HTTP a tu API. A continuación, se describen los pasos para configurar y ejecutar las pruebas.

## 1. Instalación de Dependencias

Asegúrate de tener `pytest` y `httpx` instalados. Puedes instalarlos ejecutando:

```bash
pip install pytest httpx
```

## 2. Estructura de Archivos para Pruebas

Crea un nuevo directorio llamado `tests` en la raíz de tu proyecto. Dentro de este directorio, crea un archivo llamado `test_api.py`.

```
/tu_proyecto
│
├── app
│   ├── main.py
│   ├── routers
│   │   └── tasks_router.py
│   └── db.py
│
└── tests
    └── test_api.py
```

## 3. Escribir Pruebas

A continuación, se muestra un ejemplo de cómo podrías estructurar tus pruebas en `test_api.py`:

```python
# tests/test_api.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_task():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/tasks/", json={"title": "Test Task", "description": "This is a test task", "completed": False})
    assert response.status_code == 200
    assert response.json()["title"] == "Test Task"

@pytest.mark.asyncio
async def test_get_task():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/tasks/", json={"title": "Test Task", "description": "This is a test task", "completed": False})
        task_id = response.json()["id"]
        
        response = await client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["id"] == task_id

@pytest.mark.asyncio
async def test_get_all_tasks():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/tasks/")
    assert response.status_code == 200
    assert isinstance(response.json()["tasks"], list)

@pytest.mark.asyncio
async def test_update_task():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/tasks/", json={"title": "Test Task", "description": "This is a test task", "completed": False})
        task_id = response.json()["id"]
        
        response = await client.put(f"/tasks/{task_id}", json={"title": "Updated Task", "description": "This task has been updated", "completed": True})
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Task"

@pytest.mark.asyncio
async def test_delete_task():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/tasks/", json={"title": "Test Task", "description": "This is a test task", "completed": False})
        task_id = response.json()["id"]
        
        response = await client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Task deleted successfully"

@pytest.mark.asyncio
async def test_delete_all_tasks():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete("/tasks/")
    assert response.status_code == 200
    assert response.json()["message"] == "Todas las tareas han sido eliminadas exitosamente"
```

## 4. Ejecutar las Pruebas

Para ejecutar las pruebas, navega a la raíz de tu proyecto y ejecuta el siguiente comando:

```bash
pytest tests/
```

## 5. Verificar Resultados

Después de ejecutar las pruebas, `pytest` te mostrará un resumen de las pruebas que pasaron y las que fallaron. Asegúrate de que todas las pruebas pasen para confirmar que tus operaciones funcionan correctamente.

## Conclusión

Siguiendo estos pasos, podrás implementar pruebas efectivas para tu API de gestión de tareas y asegurarte de que todas las operaciones (crear, obtener, actualizar y eliminar tareas) funcionan como se espera.
