"""
Configuración de pytest para el proyecto Sonnar
Contiene fixtures compartidas para todos los tests
"""
import pytest
import sys
import os
from datetime import datetime
import tempfile

# Agregar el directorio padre al path para importar main
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import MedicineApp
import sqlite3


@pytest.fixture
def temp_db():
    """Crea una base de datos temporal para tests"""
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db')
    db_path = temp_file.name
    temp_file.close()
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def app_instance(temp_db):
    """Crea una instancia de la aplicación con BD temporal"""
    app = MedicineApp()
    app.db_path = temp_db
    app.init_db()
    return app


@pytest.fixture
def sample_medicine():
    """Datos de ejemplo para un medicamento válido"""
    return {
        'name': 'Paracetamol',
        'time': '08:00',
        'grams': '500',
        'days': '3',
        'hours': '8',
        'total_doses': 9,
        'taken_doses': 0,
        'completed': False,
        'start_date': datetime.now().strftime("%Y-%m-%d"),
        'current_alert_time': '08:00',
        'last_notification_time': None
    }


@pytest.fixture
def multiple_medicines():
    """Lista de medicamentos para pruebas múltiples"""
    return [
        {
            'name': 'Paracetamol',
            'time': '08:00',
            'grams': '500',
            'days': '3',
            'hours': '8',
            'total_doses': 9,
            'taken_doses': 0,
            'completed': False,
            'start_date': datetime.now().strftime("%Y-%m-%d"),
            'current_alert_time': '08:00',
            'last_notification_time': None
        },
        {
            'name': 'Ibuprofeno',
            'time': '10:00',
            'grams': '400',
            'days': '5',
            'hours': '6',
            'total_doses': 20,
            'taken_doses': 5,
            'completed': False,
            'start_date': datetime.now().strftime("%Y-%m-%d"),
            'current_alert_time': '10:00',
            'last_notification_time': None
        },
        {
            'name': 'Aspirina',
            'time': '12:00',
            'grams': '100',
            'days': '7',
            'hours': '12',
            'total_doses': 14,
            'taken_doses': 14,
            'completed': True,
            'start_date': datetime.now().strftime("%Y-%m-%d"),
            'current_alert_time': '12:00',
            'last_notification_time': None
        }
    ]


@pytest.fixture
def db_connection(temp_db):
    """Conexión directa a la base de datos para tests"""
    conn = sqlite3.connect(temp_db)
    yield conn
    conn.close()


def pytest_configure(config):
    """Configuración global de pytest"""
    config.addinivalue_line(
        "markers", "unit: Pruebas unitarias de funciones individuales"
    )
    config.addinivalue_line(
        "markers", "integration: Pruebas de integración de módulos"
    )
    config.addinivalue_line(
        "markers", "functional: Pruebas funcionales end-to-end"
    )

