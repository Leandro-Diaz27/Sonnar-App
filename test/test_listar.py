"""
TST01-TST05: Tests para el módulo de Listar Medicamentos
Verifican el correcto listado y visualización de medicamentos
"""
import pytest
import sqlite3


class TestListarMedicamentos:
    """Casos de prueba para el módulo de listar medicamentos"""

    @pytest.mark.functional
    def test_listar_vacio(self, app_instance):
        """
        TST01: Verificar que la lista esté vacía inicialmente
        Datos de entrada: Base de datos sin medicamentos
        Resultado esperado: Lista vacía []
        """
        app_instance.load_medicines_from_db()
        assert len(app_instance.medicines) == 0
        assert app_instance.medicines == []

    @pytest.mark.functional
    def test_listar_un_medicamento(self, app_instance, sample_medicine):
        """
        TST02: Verificar listado con un solo medicamento
        Datos de entrada: Un medicamento en BD
        Resultado esperado: Lista con 1 elemento
        """
        # Insertar medicamento
        med_id = app_instance.insert_medicine_db(sample_medicine)
        sample_medicine['id'] = med_id
        
        # Cargar y verificar
        app_instance.load_medicines_from_db()
        assert len(app_instance.medicines) == 1
        assert app_instance.medicines[0]['name'] == 'Paracetamol'
        assert app_instance.medicines[0]['time'] == '08:00'
        assert app_instance.medicines[0]['grams'] == '500'

    @pytest.mark.functional
    def test_listar_multiples_medicamentos(self, app_instance, multiple_medicines):
        """
        TST03: Verificar listado con múltiples medicamentos
        Datos de entrada: 3 medicamentos en BD
        Resultado esperado: Lista con 3 elementos ordenados por ID DESC
        """
        # Insertar múltiples medicamentos
        for med in multiple_medicines:
            app_instance.insert_medicine_db(med)
        
        # Cargar y verificar
        app_instance.load_medicines_from_db()
        assert len(app_instance.medicines) == 3
        
        # Verificar que están ordenados por ID descendente
        assert app_instance.medicines[0]['name'] == 'Aspirina'  # Último insertado
        assert app_instance.medicines[1]['name'] == 'Ibuprofeno'
        assert app_instance.medicines[2]['name'] == 'Paracetamol'  # Primero insertado

    @pytest.mark.unit
    def test_campos_medicamento_completos(self, app_instance, sample_medicine):
        """
        TST04: Verificar que todos los campos se cargan correctamente
        Datos de entrada: Medicamento con todos los campos
        Resultado esperado: Todos los campos presentes en el objeto cargado
        """
        app_instance.insert_medicine_db(sample_medicine)
        app_instance.load_medicines_from_db()
        
        med = app_instance.medicines[0]
        campos_requeridos = ['id', 'name', 'time', 'grams', 'days', 'hours', 
                            'total_doses', 'taken_doses', 'completed', 'start_date',
                            'current_alert_time', 'last_notification_time']
        
        for campo in campos_requeridos:
            assert campo in med, f"Campo '{campo}' no encontrado en medicamento"

    @pytest.mark.unit
    def test_tipos_datos_correctos(self, app_instance, sample_medicine):
        """
        TST05: Verificar que los tipos de datos son correctos
        Datos de entrada: Medicamento con campos mixtos
        Resultado esperado: Tipos de datos correctos (int para taken_doses, bool para completed)
        """
        app_instance.insert_medicine_db(sample_medicine)
        app_instance.load_medicines_from_db()
        
        med = app_instance.medicines[0]
        assert isinstance(med['id'], int)
        assert isinstance(med['name'], str)
        assert isinstance(med['time'], str)
        assert isinstance(med['total_doses'], int)
        assert isinstance(med['taken_doses'], int)
        assert isinstance(med['completed'], bool)

    @pytest.mark.integration
    def test_listar_despues_actualizacion(self, app_instance, sample_medicine):
        """
        TST06: Verificar listado después de actualizar un medicamento
        Datos de entrada: Medicamento actualizado
        Resultado esperado: Cambios reflejados en el listado
        """
        # Insertar medicamento
        med_id = app_instance.insert_medicine_db(sample_medicine)
        sample_medicine['id'] = med_id
        
        # Actualizar
        sample_medicine['taken_doses'] = 5
        sample_medicine['completed'] = False
        app_instance.update_medicine_db(sample_medicine)
        
        # Recargar y verificar
        app_instance.load_medicines_from_db()
        assert app_instance.medicines[0]['taken_doses'] == 5

    @pytest.mark.integration
    def test_listar_con_medicamentos_completados(self, app_instance, multiple_medicines):
        """
        TST07: Verificar que se listan medicamentos completados y no completados
        Datos de entrada: Medicamentos con diferentes estados
        Resultado esperado: Todos aparecen en la lista
        """
        for med in multiple_medicines:
            app_instance.insert_medicine_db(med)
        
        app_instance.load_medicines_from_db()
        
        completados = [m for m in app_instance.medicines if m['completed']]
        no_completados = [m for m in app_instance.medicines if not m['completed']]
        
        assert len(completados) == 1
        assert len(no_completados) == 2
        assert len(app_instance.medicines) == 3

