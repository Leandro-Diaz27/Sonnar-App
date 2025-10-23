"""
TST18-TST25: Tests para el módulo de Persistencia de Datos
Verifican el correcto guardado y recuperación de datos en SQLite
"""
import pytest
import sqlite3
import os


class TestPersistenciaDatos:
    """Casos de prueba para la persistencia en base de datos"""

    @pytest.mark.unit
    def test_creacion_base_datos(self, app_instance, temp_db):
        """
        TST18: Verificar que la base de datos se crea correctamente
        Datos de entrada: Inicialización de app
        Resultado esperado: Archivo .db creado con tabla medicamentos
        """
        assert os.path.exists(temp_db)
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        # Verificar que la tabla existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='medicamentos'
        """)
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[0] == 'medicamentos'

    @pytest.mark.unit
    def test_esquema_tabla_correcto(self, app_instance, temp_db):
        """
        TST19: Verificar que el esquema de la tabla es correcto
        Datos de entrada: Base de datos inicializada
        Resultado esperado: Columnas correctas con tipos de datos adecuados
        """
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(medicamentos)")
        columns = cursor.fetchall()
        conn.close()
        
        column_names = [col[1] for col in columns]
        expected_columns = [
            'id', 'name', 'time', 'grams', 'days', 'hours',
            'total_doses', 'taken_doses', 'completed', 'start_date',
            'current_alert_time', 'last_notification_time'
        ]
        
        for expected_col in expected_columns:
            assert expected_col in column_names, f"Columna '{expected_col}' no encontrada"

    @pytest.mark.unit
    def test_indice_unico_creado(self, app_instance, temp_db):
        """
        TST20: Verificar que el índice único (name, time) existe
        Datos de entrada: Base de datos inicializada
        Resultado esperado: Índice idx_meds_name_time existe
        """
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name='idx_meds_name_time'
        """)
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None

    @pytest.mark.integration
    def test_insercion_persiste_datos(self, app_instance, sample_medicine):
        """
        TST21: Verificar que los datos insertados persisten
        Datos de entrada: Medicamento insertado
        Resultado esperado: Datos recuperables después de inserción
        """
        # Insertar
        med_id = app_instance.insert_medicine_db(sample_medicine)
        
        # Recuperar directamente de BD
        conn = sqlite3.connect(app_instance.get_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM medicamentos WHERE id=?", (med_id,))
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[1] == 'Paracetamol'  # name
        assert result[2] == '08:00'  # time

    @pytest.mark.integration
    def test_actualizacion_persiste_cambios(self, app_instance, sample_medicine):
        """
        TST22: Verificar que las actualizaciones persisten
        Datos de entrada: Medicamento actualizado
        Resultado esperado: Cambios guardados en BD
        """
        # Insertar
        med_id = app_instance.insert_medicine_db(sample_medicine)
        sample_medicine['id'] = med_id
        
        # Actualizar
        sample_medicine['taken_doses'] = 7
        sample_medicine['completed'] = False
        app_instance.update_medicine_db(sample_medicine)
        
        # Verificar en BD
        conn = sqlite3.connect(app_instance.get_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT taken_doses, completed FROM medicamentos WHERE id=?", (med_id,))
        result = cursor.fetchone()
        conn.close()
        
        assert result[0] == 7
        assert result[1] == 0  # False

    @pytest.mark.integration
    def test_carga_persistente_al_reiniciar(self, app_instance, multiple_medicines):
        """
        TST23: Verificar que los datos persisten al recargar la app
        Datos de entrada: Múltiples medicamentos guardados
        Resultado esperado: Datos disponibles después de recargar
        """
        # Insertar medicamentos
        for med in multiple_medicines:
            app_instance.insert_medicine_db(med)
        
        # Simular cierre y apertura de app
        app_instance.medicines = []
        app_instance.load_medicines_from_db()
        
        assert len(app_instance.medicines) == 3
        assert app_instance.medicines[0]['name'] in ['Paracetamol', 'Ibuprofeno', 'Aspirina']

    @pytest.mark.integration
    def test_integridad_datos_completos(self, app_instance, sample_medicine):
        """
        TST24: Verificar integridad de todos los campos
        Datos de entrada: Medicamento con todos los campos
        Resultado esperado: Todos los datos se guardan y recuperan correctamente
        """
        # Insertar
        med_id = app_instance.insert_medicine_db(sample_medicine)
        
        # Recuperar
        app_instance.load_medicines_from_db()
        med_recovered = app_instance.medicines[0]
        
        assert med_recovered['name'] == sample_medicine['name']
        assert med_recovered['time'] == sample_medicine['time']
        assert med_recovered['grams'] == sample_medicine['grams']
        assert str(med_recovered['days']) == sample_medicine['days']
        assert str(med_recovered['hours']) == sample_medicine['hours']
        assert med_recovered['total_doses'] == sample_medicine['total_doses']
        assert med_recovered['taken_doses'] == sample_medicine['taken_doses']

    @pytest.mark.integration
    def test_actualizacion_parcial(self, app_instance, sample_medicine):
        """
        TST25: Verificar actualización parcial de campos
        Datos de entrada: Actualizar solo taken_doses
        Resultado esperado: Solo ese campo cambia, el resto permanece igual
        """
        # Insertar
        med_id = app_instance.insert_medicine_db(sample_medicine)
        sample_medicine['id'] = med_id
        
        # Guardar valores originales
        original_name = sample_medicine['name']
        original_time = sample_medicine['time']
        
        # Actualizar solo taken_doses
        sample_medicine['taken_doses'] = 3
        app_instance.update_medicine_db(sample_medicine)
        
        # Verificar
        app_instance.load_medicines_from_db()
        med = app_instance.medicines[0]
        
        assert med['taken_doses'] == 3
        assert med['name'] == original_name
        assert med['time'] == original_time

    @pytest.mark.unit
    def test_manejo_valores_null(self, app_instance):
        """
        TST26: Verificar manejo de valores NULL
        Datos de entrada: last_notification_time = NULL
        Resultado esperado: Se maneja correctamente como None
        """
        medicamento = {
            'name': 'Loratadina',
            'time': '07:00',
            'grams': '10',
            'days': '10',
            'hours': '24',
            'total_doses': 10,
            'taken_doses': 0,
            'completed': False,
            'start_date': '2025-10-23',
            'current_alert_time': '07:00',
            'last_notification_time': None
        }
        
        app_instance.insert_medicine_db(medicamento)
        app_instance.load_medicines_from_db()
        
        med = app_instance.medicines[0]
        assert med['last_notification_time'] is None

    @pytest.mark.integration
    def test_transacciones_atomicas(self, app_instance, temp_db):
        """
        TST27: Verificar que las operaciones son atómicas
        Datos de entrada: Inserción múltiple
        Resultado esperado: O todas se guardan o ninguna
        """
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        try:
            # Intentar insertar múltiples registros
            cursor.execute("""
                INSERT INTO medicamentos (name, time, grams, days, hours, total_doses, taken_doses, completed, start_date, current_alert_time)
                VALUES ('Med1', '08:00', '100', 5, 8, 15, 0, 0, '2025-10-23', '08:00')
            """)
            cursor.execute("""
                INSERT INTO medicamentos (name, time, grams, days, hours, total_doses, taken_doses, completed, start_date, current_alert_time)
                VALUES ('Med2', '10:00', '200', 3, 12, 6, 0, 0, '2025-10-23', '10:00')
            """)
            conn.commit()
        except Exception as e:
            conn.rollback()
            pytest.fail(f"Transacción falló: {e}")
        finally:
            conn.close()
        
        # Verificar que ambos se guardaron
        app_instance.load_medicines_from_db()
        assert len(app_instance.medicines) >= 2

