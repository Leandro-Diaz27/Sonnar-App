"""
TST08-TST15: Tests para el módulo de Agregar Medicamentos
Verifican que los medicamentos se agreguen correctamente
"""
import pytest
from datetime import datetime


class TestAgregarMedicamentos:
    """Casos de prueba para el módulo de agregar medicamentos"""

    @pytest.mark.functional
    def test_agregar_medicamento_valido(self, app_instance, sample_medicine):
        """
        TST08: Agregar medicamento con datos válidos
        Datos de entrada: name='Paracetamol', time='08:00', grams='500', days='3', hours='8'
        Resultado esperado: Medicamento agregado exitosamente con ID asignado
        """
        med_id = app_instance.insert_medicine_db(sample_medicine)
        
        assert med_id is not None
        assert med_id > 0
        
        # Verificar en BD
        app_instance.load_medicines_from_db()
        assert len(app_instance.medicines) == 1
        assert app_instance.medicines[0]['name'] == 'Paracetamol'

    @pytest.mark.unit
    def test_validacion_formato_hora(self, app_instance):
        """
        TST09: Validar formato de hora HH:MM
        Datos de entrada: Diferentes formatos de hora
        Resultado esperado: True para formato válido, False para inválido
        """
        assert app_instance.is_valid_time_format('08:00') == True
        assert app_instance.is_valid_time_format('23:59') == True
        assert app_instance.is_valid_time_format('00:00') == True
        assert app_instance.is_valid_time_format('8:00') == True  # Python acepta sin cero inicial
        assert app_instance.is_valid_time_format('25:00') == False  # Hora inválida
        assert app_instance.is_valid_time_format('08:60') == False  # Minuto inválido
        assert app_instance.is_valid_time_format('08-30') == False  # Separador incorrecto
        assert app_instance.is_valid_time_format('abc') == False

    @pytest.mark.unit
    def test_calculo_dosis_totales(self, app_instance):
        """
        TST10: Verificar cálculo de dosis totales
        Datos de entrada: days=3, hours=8
        Resultado esperado: total_doses = ceil((3 * 24) / 8) = 9
        """
        total = app_instance.calculate_doses('3', '8')
        assert total == 9
        
        total = app_instance.calculate_doses('5', '6')
        assert total == 20
        
        total = app_instance.calculate_doses('7', '12')
        assert total == 14

    @pytest.mark.unit
    def test_calculo_dosis_valores_invalidos(self, app_instance):
        """
        TST11: Verificar manejo de valores inválidos en cálculo de dosis
        Datos de entrada: Valores negativos, cero, no numéricos
        Resultado esperado: Retorna 0
        """
        assert app_instance.calculate_doses('0', '8') == 0
        assert app_instance.calculate_doses('3', '0') == 0
        assert app_instance.calculate_doses('-1', '8') == 0
        assert app_instance.calculate_doses('abc', '8') == 0
        assert app_instance.calculate_doses('3', 'xyz') == 0

    @pytest.mark.functional
    def test_prevenir_duplicados(self, app_instance, sample_medicine):
        """
        TST12: Verificar que no se permiten duplicados (mismo nombre + hora)
        Datos de entrada: Mismo medicamento insertado dos veces
        Resultado esperado: Solo se inserta una vez (INSERT OR IGNORE)
        """
        # Primera inserción
        med_id1 = app_instance.insert_medicine_db(sample_medicine)
        
        # Segunda inserción (duplicado)
        med_id2 = app_instance.insert_medicine_db(sample_medicine)
        
        # Ambos IDs deberían ser el mismo (el original)
        assert med_id1 == med_id2
        
        # Verificar que solo hay un registro
        app_instance.load_medicines_from_db()
        assert len(app_instance.medicines) == 1

    @pytest.mark.functional
    def test_agregar_mismo_medicamento_diferente_hora(self, app_instance, sample_medicine):
        """
        TST13: Verificar que se puede agregar el mismo medicamento con diferente hora
        Datos de entrada: Paracetamol a las 08:00 y a las 14:00
        Resultado esperado: Dos registros diferentes
        """
        # Primer medicamento
        med_id1 = app_instance.insert_medicine_db(sample_medicine)
        
        # Mismo medicamento, diferente hora
        sample_medicine2 = sample_medicine.copy()
        sample_medicine2['time'] = '14:00'
        sample_medicine2['current_alert_time'] = '14:00'
        med_id2 = app_instance.insert_medicine_db(sample_medicine2)
        
        assert med_id1 != med_id2
        
        # Verificar que hay dos registros
        app_instance.load_medicines_from_db()
        assert len(app_instance.medicines) == 2

    @pytest.mark.integration
    def test_agregar_multiples_medicamentos(self, app_instance, multiple_medicines):
        """
        TST14: Agregar múltiples medicamentos diferentes
        Datos de entrada: 3 medicamentos distintos
        Resultado esperado: 3 registros en la base de datos
        """
        ids = []
        for med in multiple_medicines:
            med_id = app_instance.insert_medicine_db(med)
            ids.append(med_id)
        
        # Verificar que todos tienen IDs únicos
        assert len(set(ids)) == 3
        
        # Verificar en BD
        app_instance.load_medicines_from_db()
        assert len(app_instance.medicines) == 3

    @pytest.mark.unit
    def test_valores_iniciales_correctos(self, app_instance, sample_medicine):
        """
        TST15: Verificar que los valores iniciales son correctos al agregar
        Datos de entrada: Medicamento nuevo
        Resultado esperado: taken_doses=0, completed=False, start_date=hoy
        """
        app_instance.insert_medicine_db(sample_medicine)
        app_instance.load_medicines_from_db()
        
        med = app_instance.medicines[0]
        assert med['taken_doses'] == 0
        assert med['completed'] == False
        assert med['start_date'] == datetime.now().strftime("%Y-%m-%d")
        assert med['current_alert_time'] == med['time']

    @pytest.mark.integration
    def test_medicamento_en_lista_predefinida(self, app_instance):
        """
        TST16: Verificar que se puede obtener información de medicamentos predefinidos
        Datos de entrada: Nombre de medicamento de la lista
        Resultado esperado: Información completa del medicamento
        """
        info = app_instance.get_medication_info('Paracetamol')
        
        assert info is not None
        assert info['name'] == 'Paracetamol'
        assert info['typical_dose'] == '500mg'
        assert 'description' in info
        
        # Medicamento no existente
        info_none = app_instance.get_medication_info('MedicamentoInexistente')
        assert info_none is None

    @pytest.mark.functional
    def test_agregar_con_calculo_automatico_dosis(self, app_instance):
        """
        TST17: Verificar que el cálculo de dosis se realiza automáticamente
        Datos de entrada: days=5, hours=12
        Resultado esperado: total_doses calculado automáticamente (10 dosis)
        """
        medicamento = {
            'name': 'Omeprazol',
            'time': '09:00',
            'grams': '20',
            'days': '5',
            'hours': '12',
            'total_doses': app_instance.calculate_doses('5', '12'),
            'taken_doses': 0,
            'completed': False,
            'start_date': datetime.now().strftime("%Y-%m-%d"),
            'current_alert_time': '09:00',
            'last_notification_time': None
        }
        
        app_instance.insert_medicine_db(medicamento)
        app_instance.load_medicines_from_db()
        
        med = app_instance.medicines[0]
        assert med['total_doses'] == 10  # (5 * 24) / 12 = 10

