from kivy.config import Config
Config.set('graphics', 'width', '390')
Config.set('graphics', 'height', '900')
Config.set('graphics', 'resizable', False)

from kivy.lang import Builder
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivymd.app import MDApp
from kivymd.uix.navigationbar import MDNavigationItem
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDButton, MDButtonText, MDButtonIcon
from kivymd.uix.list import (
    MDListItem,
    MDListItemHeadlineText,
    MDListItemSupportingText,
    MDListItemLeadingIcon,
    MDListItemTrailingIcon,
)
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogSupportingText, MDDialogButtonContainer
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.progressindicator import MDLinearProgressIndicator
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDButton
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, Line
from datetime import datetime, timedelta
import sqlite3
import os
import math


class BaseMDNavigationItem(MDNavigationItem):
    icon = StringProperty()
    text = StringProperty()


class MedicineScreen(MDScreen):
    pass


class AddMedicineScreen(MDScreen):
    pass


class MedicineApp(MDApp):
    medicines = ListProperty([])
    dialog = None
    selected_medication = StringProperty("")
    db_path = StringProperty("")
    
    # Lista de medicamentos
    MEDICATIONS_LIST = [
        {"name": "Paracetamol", "typical_dose": "500mg", "description": "Analgésico y antipirético"},
        {"name": "Ibuprofeno", "typical_dose": "400mg", "description": "Antiinflamatorio no esteroideo"},
        {"name": "Aspirina", "typical_dose": "100mg", "description": "Analgésico y antiagregante plaquetario"},
        {"name": "Omeprazol", "typical_dose": "20mg", "description": "Inhibidor de bomba de protones"},
        {"name": "Loratadina", "typical_dose": "10mg", "description": "Antihistamínico para alergias"},
        {"name": "Amoxicilina", "typical_dose": "500mg", "description": "Antibiótico de amplio espectro"},
        {"name": "Metformina", "typical_dose": "500mg", "description": "Antidiabético oral"},
        {"name": "Losartán", "typical_dose": "50mg", "description": "Antihipertensivo"},
        {"name": "Atorvastatina", "typical_dose": "20mg", "description": "Hipolipemiante"},
        {"name": "Levotiroxina", "typical_dose": "50mcg", "description": "Hormona tiroidea"},
        {"name": "Clonazepam", "typical_dose": "0.5mg", "description": "Ansiolítico y anticonvulsivo"},
        {"name": "Sertralina", "typical_dose": "50mg", "description": "Antidepresivo"},
        {"name": "Diclofenaco", "typical_dose": "50mg", "description": "Antiinflamatorio y analgésico"},
        {"name": "Ranitidina", "typical_dose": "150mg", "description": "Antagonista H2"},
        {"name": "Prednisona", "typical_dose": "5mg", "description": "Corticoide antiinflamatorio"}
    ]

    def build(self):
        self.title = "Sonnar"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"  # Volver a tema claro
        self.theme_cls.accent_palette = "Teal"
        return Builder.load_file("medicamentos.kv")

    # ====== Persistencia: SQLite ======
    def get_db_path(self):
        if not self.db_path:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.db_path = os.path.join(base_dir, "medicamentos.db")
        return self.db_path

    def init_db(self):
        conn = sqlite3.connect(self.get_db_path())
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS medicamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                time TEXT NOT NULL,
                grams TEXT NOT NULL,
                days INTEGER NOT NULL,
                hours INTEGER NOT NULL,
                total_doses INTEGER NOT NULL,
                taken_doses INTEGER NOT NULL DEFAULT 0,
                completed INTEGER NOT NULL DEFAULT 0,
                start_date TEXT,
                current_alert_time TEXT,
                last_notification_time TEXT
            )
            """
        )
        # Índice para evitar duplicados lógicos (name+time)
        cur.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_meds_name_time
            ON medicamentos(name, time)
            """
        )
        conn.commit()
        conn.close()

    def load_medicines_from_db(self):
        conn = sqlite3.connect(self.get_db_path())
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, name, time, grams, days, hours, total_doses, taken_doses,
                   completed, start_date, current_alert_time, last_notification_time
            FROM medicamentos
            ORDER BY id DESC
            """
        )
        rows = cur.fetchall()
        conn.close()

        loaded = []
        for r in rows:
            med = {
                'id': r[0],
                'name': r[1],
                'time': r[2],
                'grams': r[3],
                'days': str(r[4]),
                'hours': str(r[5]),
                'total_doses': int(r[6]) if r[6] is not None else 0,
                'taken_doses': int(r[7]) if r[7] is not None else 0,
                'completed': bool(r[8]),
                'start_date': r[9] or datetime.now().strftime("%Y-%m-%d"),
                'current_alert_time': r[10] or r[2],
                'last_notification_time': r[11],
                'taken': False,
            }
            loaded.append(med)
        self.medicines = loaded

    def insert_medicine_db(self, med_dict):
        conn = sqlite3.connect(self.get_db_path())
        cur = conn.cursor()
        cur.execute(
            """
            INSERT OR IGNORE INTO medicamentos
            (name, time, grams, days, hours, total_doses, taken_doses, completed,
             start_date, current_alert_time, last_notification_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                med_dict['name'],
                med_dict['time'],
                med_dict['grams'],
                int(med_dict['days']),
                int(med_dict['hours']),
                int(med_dict.get('total_doses', 0)),
                int(med_dict.get('taken_doses', 0)),
                1 if med_dict.get('completed', False) else 0,
                med_dict.get('start_date'),
                med_dict.get('current_alert_time', med_dict['time']),
                med_dict.get('last_notification_time'),
            ),
        )
        # Si fue ignorado por duplicado, obtenemos el id existente
        if cur.rowcount == 0:
            cur.execute(
                "SELECT id FROM medicamentos WHERE name=? AND time=?",
                (med_dict['name'], med_dict['time']),
            )
            row = cur.fetchone()
            new_id = row[0] if row else None
        else:
            new_id = cur.lastrowid
        conn.commit()
        conn.close()
        return new_id

    def update_medicine_db(self, med_dict):
        if 'id' not in med_dict or med_dict['id'] is None:
            return
        conn = sqlite3.connect(self.get_db_path())
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE medicamentos
            SET grams=?, days=?, hours=?, total_doses=?, taken_doses=?,
                completed=?, start_date=?, current_alert_time=?, last_notification_time=?
            WHERE id=?
            """,
            (
                med_dict['grams'],
                int(med_dict['days']),
                int(med_dict['hours']),
                int(med_dict.get('total_doses', 0)),
                int(med_dict.get('taken_doses', 0)),
                1 if med_dict.get('completed', False) else 0,
                med_dict.get('start_date'),
                med_dict.get('current_alert_time', med_dict['time']),
                med_dict.get('last_notification_time'),
                int(med_dict['id']),
            ),
        )
        conn.commit()
        conn.close()

    def calculate_doses(self, days, hours):
        """Calcula el número total de dosis basado en días y frecuenc.asaia en horas"""
        try:
            days_int = int(days)
            hours_int = int(hours)
            if days_int <= 0 or hours_int <= 0:
                return 0
            # Calcular dosis totales: (días * 24 horas) / frecuencia en horas
            total_doses = math.ceil((days_int * 24) / hours_int)
            return total_doses
        except (ValueError, TypeError):
            return 0

    def get_medication_progress(self, med):
        """Calcula el progreso del medicamento basado en las dosis tomadas"""
        try:
            days_int = int(med['days'])
            hours_int = int(med['hours'])
            
            if days_int <= 0 or hours_int <= 0:
                return 0, 0, 0
            
            # Calcular dosis totales
            total_doses = self.calculate_doses(med['days'], med['hours'])
            
            # Dosis tomadas (usar el campo correcto)
            taken_doses = med.get('taken_doses', 0)
            
            # Dosis esperadas (basado en tiempo transcurrido)
            start_time = datetime.now().replace(hour=int(med['time'].split(':')[0]), 
                                              minute=int(med['time'].split(':')[1]), 
                                              second=0, microsecond=0)
            
            # Si ya pasó la hora de hoy, empezar desde ayer
            if start_time > datetime.now():
                start_time -= timedelta(days=1)
            
            elapsed_hours = (datetime.now() - start_time).total_seconds() / 3600
            expected_doses = min(math.floor(elapsed_hours / hours_int) + 1, total_doses)
            
            return total_doses, expected_doses, taken_doses
        except Exception:
            return 0, 0, 0

    def calculate_next_dose_time(self, med):
        """Calcula la hora de la próxima dosis basada en la última dosis tomada"""
        try:
            # Obtener la hora de inicio del medicamento
            start_time_str = med.get('time', '00:00')
            start_hour, start_minute = map(int, start_time_str.split(':'))
            
            # Calcular cuántas dosis se han tomado
            taken_doses = med.get('taken_doses', 0)
            hours_interval = int(med.get('hours', 1))
            
            # Calcular la hora de la próxima dosis
            next_dose_hour = (start_hour + (taken_doses * hours_interval)) % 24
            next_dose_minute = start_minute
            
            return f"{next_dose_hour:02d}:{next_dose_minute:02d}"
        except:
            return med.get('time', '00:00')

    def on_switch_tabs(self, bar, item, icon, text):
        self.root.ids.screen_manager.current = text

    def show_medication_menu(self, button):
        """Muestra el menú desplegable de medicamentos"""
        menu_items = []
        for med in self.MEDICATIONS_LIST:
            menu_items.append({
                "text": f"{med['name']} ({med['typical_dose']})",
                "on_release": lambda x=None, medication=med: self.select_medication(medication),
            })
        MDDropdownMenu(
            caller=button,
            items=menu_items,
        ).open()

    def select_medication(self, medication):
        """Selecciona un medicamento de la lista"""
        self.selected_medication = medication['name']
        add_screen = self.root.ids.screen_manager.get_screen("Agregar")
        # Actualizar el texto del botón
        add_screen.ids.med_name.children[0].text = f"✓ {medication['name']} ({medication['typical_dose']})"
        self.on_text_fields_change()  # Actualizar estado del botón

    def get_medication_info(self, name):
        """Obtiene información de un medicamento por nombre"""
        for med in self.MEDICATIONS_LIST:
            if med['name'] == name:
                return med
        return None

    def is_valid_time_format(self, time_str):
        try:
            datetime.strptime(time_str, "%H:%M")
            return True
        except Exception:
            return False

    def reset_add_screen(self):
        add_screen = self.root.ids.screen_manager.get_screen("Agregar")
        add_screen.ids.med_name.children[0].text = "Toca para seleccionar medicamento"
        add_screen.ids.med_time.text = ""
        add_screen.ids.med_grm.text = ""
        add_screen.ids.med_days.text = ""
        add_screen.ids.med_hours.text = ""
        add_screen.ids.save_button.disabled = True
        self.selected_medication = ""

    def save_medicine(self):
        add_screen = self.root.ids.screen_manager.get_screen("Agregar")
        name = self.selected_medication
        time = add_screen.ids.med_time.text.strip()
        grams = add_screen.ids.med_grm.text.strip()
        days = add_screen.ids.med_days.text.strip()
        hours = add_screen.ids.med_hours.text.strip()

        if not name or not time or not grams or not days or not hours:
            self.show_info_dialog("Por favor, completa todos los campos.")
            return

        if not self.is_valid_time_format(time):
            self.show_info_dialog("⏰ Formato inválido.\nUsa HH:MM (ejemplo: 08:30).")
            return

        if any(med['name'] == name and med['time'] == time for med in self.medicines):
            self.show_info_dialog("⚠️ Este medicamento ya está registrado.")
            return

        # Calcular dosis totales
        total_doses = self.calculate_doses(days, hours)

        new_med = {
            'name': name,
            'time': time,
            'grams': grams,
            'days': days,
            'hours': hours,
            'taken': False,
            'total_doses': total_doses,
            'taken_doses': 0,
            'completed': False,
            'last_notification': None,
            'last_notification_time': None,
            'start_date': datetime.now().strftime("%Y-%m-%d"),
            'current_alert_time': time
        }
        # Guardar en SQLite y recuperar id
        new_id = self.insert_medicine_db(new_med)
        new_med['id'] = new_id
        self.medicines.append(new_med)
        self.update_meds_list()
        self.reset_add_screen()
        self.root.ids.screen_manager.current = "Medicamentos"

    def update_meds_list(self):
        """Refresca la lista en la pantalla Medicamentos."""
        med_screen = self.root.ids.screen_manager.get_screen("Medicamentos")
        meds_box = med_screen.ids.meds_box
        meds_box.clear_widgets()

        from kivy.metrics import dp

        # Si no hay medicamentos, mostrar mensaje
        if not self.medicines:
            self.show_empty_state(meds_box)
            return

        for med in self.medicines:
            # Calcular progreso actual
            total_doses, expected_doses, taken_doses = self.get_medication_progress(med)
            
            # Actualizar solo total_doses, no sobrescribir taken_doses
            med['total_doses'] = total_doses
            
            # Calcular próxima dosis basada en la frecuencia del medicamento
            # Solo usar el tiempo de alerta actual si el medicamento está retrasado y no se ha tomado
            if med.get('current_alert_time', med['time']) != med['time'] and not med.get('taken', False):
                # Si está retrasado y no se ha tomado, mostrar el tiempo retrasado
                next_dose_time = med.get('current_alert_time', med['time'])
            else:
                # Si ya se tomó o no está retrasado, calcular la próxima dosis normal
                next_dose_time = self.calculate_next_dose_time(med)
            
            # Crear contenedor para cada medicamento
            from kivymd.uix.boxlayout import MDBoxLayout
            from kivymd.uix.label import MDLabel
            from kivymd.uix.card import MDCard
            
            # Determinar el color de la card basado en el progreso
            progress_value = taken_doses / total_doses if total_doses > 0 else 0
            if progress_value >= 1.0:
                card_color = (0.9, 0.98, 0.9, 1)  # Verde muy claro para completado
                border_color = (0.2, 0.7, 0.2, 1)
            elif progress_value > 0.5:
                card_color = (0.95, 0.97, 1, 1)  # Azul muy claro para en progreso
                border_color = (0.2, 0.6, 0.9, 1)
            else:
                card_color = (1, 0.98, 0.95, 1)  # Naranja muy claro para pendiente
                border_color = (0.9, 0.6, 0.2, 1)
            
            # Contenedor principal del medicamento con diseño mejorado
            med_container = MDCard(
                orientation='vertical',
                size_hint_y=None,
                height=dp(170),  # Altura optimizada
                padding=[dp(16), dp(12), dp(16), dp(12)],  # Padding reducido
                spacing=dp(8),  # Espaciado reducido
                md_bg_color=card_color,
                radius=[dp(16), dp(16), dp(16), dp(16)],
                elevation=3,
                line_color=border_color,
                line_width=1
            )
            
            # Fila superior: Icono pastilla, nombre y mg con diseño optimizado
            top_row = MDBoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(45),  # Altura reducida
                spacing=dp(8),  # Espaciado reducido
                pos_hint={'center_y': 0.5}
            )
            
            # Icono de pastilla sin fondo circular
            pill_icon = Image(
                source="images/pastilla2.png",
                size_hint_x=None,
                width=dp(24),  # Ligeramente más grande sin contenedor
                height=dp(24),  # Ligeramente más grande sin contenedor
                pos_hint={'center_y': 0.5}
            )
            top_row.add_widget(pill_icon)
            
            # Contenedor del nombre del medicamento
            name_container = MDBoxLayout(
                orientation='vertical',
                size_hint_x=1,
                spacing=dp(1)  # Espaciado mínimo
            )
            
            # Nombre del medicamento con contraste moderado
            med_name = MDLabel(
                text=med['name'].title(),
                theme_text_color="Custom",
                text_color=(0.15, 0.15, 0.15, 1),  # Negro suave
                font_size="16sp",
                bold=True,
                size_hint_x=1,
                halign="left",
                size_hint_y=None,
                height=dp(20)
            )
            
            # Información adicional del medicamento con contraste moderado
            med_info = MDLabel(
                text=f"Dosis: {med.get('taken_doses', 0)}/{med.get('total_doses', 0)}",
                theme_text_color="Custom",
                text_color=(0.3, 0.3, 0.3, 1),  # Gris oscuro moderado
                font_size="11sp",
                bold=True,
                size_hint_x=1,
                halign="left",
                size_hint_y=None,
                height=dp(16)
            )
            
            name_container.add_widget(med_name)
            name_container.add_widget(med_info)
            top_row.add_widget(name_container)
            
            # Tag de dosis optimizado
            dose_tag = MDBoxLayout(
                size_hint_x=None,
                width=dp(60),  # Reducido
                height=dp(30),  # Reducido
                md_bg_color=border_color,
                radius=[dp(15), dp(15), dp(15), dp(15)],
                padding=[dp(6), dp(4), dp(6), dp(4)],  # Padding reducido
                pos_hint={'center_y': 0.5}
            )
            dose_label = MDLabel(
                text=f"{med['grams']}g",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                font_size="12sp",  # Reducido
                bold=True,
                halign='center'
            )
            dose_tag.add_widget(dose_label)
            top_row.add_widget(dose_tag)
            
            med_container.add_widget(top_row)
            
            # Contenedor para la barra de progreso optimizada
            progress_container = MDBoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=dp(40),  # Altura reducida
                spacing=dp(6)  # Espaciado reducido
            )
            
            # Información de progreso con porcentaje
            progress_info = MDBoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(16),  # Altura reducida
                spacing=dp(8)  # Espaciado reducido
            )
            
            # Texto de progreso con contraste moderado
            progress_text = MDLabel(
                text="Progreso",
                theme_text_color="Custom",
                text_color=(0.2, 0.2, 0.2, 1),  # Gris oscuro moderado
                font_size="11sp",
                bold=True,
                size_hint_x=1,
                halign="left"
            )
            
            # Porcentaje con contraste moderado
            percentage = int(progress_value * 100) if total_doses > 0 else 0
            percentage_text = MDLabel(
                text=f"{percentage}%",
                theme_text_color="Custom",
                text_color=(0.15, 0.15, 0.15, 1),  # Negro suave
                font_size="11sp",
                bold=True,
                size_hint_x=None,
                width=dp(35),
                halign="right"
            )
            
            progress_info.add_widget(progress_text)
            progress_info.add_widget(percentage_text)
            progress_container.add_widget(progress_info)
            
            # Barra de progreso personalizada optimizada
            progress_bar_container = MDBoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(6),  # Altura reducida
                md_bg_color=(0.85, 0.85, 0.85, 1),
                radius=[dp(3), dp(3), dp(3), dp(3)]  # Radio reducido
            )
            
            # Parte llena de la barra con gradiente de color
            if progress_value > 0:
                filled_width = progress_value
                
                # Color basado en el progreso
                if progress_value >= 1.0:
                    progress_color = (0.2, 0.7, 0.2, 1)  # Verde para completado
                elif progress_value > 0.5:
                    progress_color = (0.2, 0.6, 0.9, 1)  # Azul para en progreso
                else:
                    progress_color = (0.9, 0.6, 0.2, 1)  # Naranja para pendiente
                
                # Parte llena
                filled_part = MDBoxLayout(
                    size_hint_x=filled_width,
                    md_bg_color=progress_color,
                    radius=[dp(4), 0, 0, dp(4)] if filled_width < 1 else [dp(4), dp(4), dp(4), dp(4)]
                )
                progress_bar_container.add_widget(filled_part)
                
                # Parte vacía
                if filled_width < 1:
                    empty_part = MDBoxLayout(
                        size_hint_x=1 - filled_width,
                        md_bg_color=(0.85, 0.85, 0.85, 1),
                        radius=[0, dp(4), dp(4), 0]
                    )
                    progress_bar_container.add_widget(empty_part)
            else:
                # Barra completamente vacía
                empty_bar = MDBoxLayout(
                    size_hint_x=1,
                    md_bg_color=(0.85, 0.85, 0.85, 1),
                    radius=[dp(4), dp(4), dp(4), dp(4)]
                )
                progress_bar_container.add_widget(empty_bar)
            
            progress_container.add_widget(progress_bar_container)
            
            # Información de horarios y frecuencia optimizada
            schedule_container = MDBoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=dp(50),  # Altura reducida
                spacing=dp(6)  # Espaciado reducido
            )
            
            # Próxima dosis con reloj optimizado
            next_dose_row = MDBoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(22),  # Altura reducida
                spacing=dp(6)  # Espaciado reducido
            )
            
            # Icono de reloj sin fondo circular
            clock_icon = Image(
                source="images/reloj.png",
                size_hint_x=None,
                width=dp(14),  # Ligeramente más grande sin contenedor
                height=dp(14),  # Ligeramente más grande sin contenedor
                pos_hint={'center_y': 0.5}
            )
            next_dose_row.add_widget(clock_icon)
            
            # Texto de próxima dosis con indicador de retraso
            delay_indicator = ""
            time_color = (0.4, 0.4, 0.4, 1)
            if med.get('current_alert_time', med['time']) != med['time']:
                delay_indicator = " (Retrasado)"
                time_color = (0.9, 0.4, 0.2, 1)
            
            next_dose_text = MDLabel(
                text=f"Próxima dosis: {next_dose_time}{delay_indicator}",
                theme_text_color="Custom",
                text_color=(0.2, 0.2, 0.2, 1) if not delay_indicator else (0.7, 0.3, 0.0, 1),  # Gris oscuro o naranja moderado
                font_size="12sp",
                bold=True,
                size_hint_x=1,
                halign="left"
            )
            next_dose_row.add_widget(next_dose_text)
            schedule_container.add_widget(next_dose_row)
            
            # Información de frecuencia y días con iconos optimizada
            frequency_row = MDBoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(22),  # Altura reducida
                spacing=dp(12)  # Espaciado reducido
            )
            
            # Cada cuántas horas
            hours_info = MDBoxLayout(
                orientation='horizontal',
                size_hint_x=0.5,
                spacing=dp(3)  # Espaciado reducido
            )
            hours_icon = MDLabel(
                text="⏰",
                font_size="10sp",  # Reducido
                size_hint_x=None,
                width=dp(16)  # Reducido
            )
            hours_text = MDLabel(
                text=f"Cada {med['hours']}h",
                theme_text_color="Custom",
                text_color=(0.35, 0.35, 0.35, 1),  # Gris oscuro moderado
                font_size="10sp",
                bold=True,
                size_hint_x=1,
                halign="left"
            )
            hours_info.add_widget(hours_icon)
            hours_info.add_widget(hours_text)
            
            # Días restantes
            days_info = MDBoxLayout(
                orientation='horizontal',
                size_hint_x=0.5,
                spacing=dp(3)
            )
            days_icon = MDLabel(
                text="📅",
                font_size="10sp",
                size_hint_x=None,
                width=dp(16)
            )
            days_text = MDLabel(
                text=f"{med['days']} días restantes",
                theme_text_color="Custom",
                text_color=(0.35, 0.35, 0.35, 1),  # Gris oscuro moderado
                font_size="10sp",
                bold=True,
                size_hint_x=1,
                halign="left"
            )
            days_info.add_widget(days_icon)
            days_info.add_widget(days_text)
            
            frequency_row.add_widget(hours_info)
            frequency_row.add_widget(days_info)
            schedule_container.add_widget(frequency_row)
            
            med_container.add_widget(schedule_container)
            
            # Barra de progreso (abajo del todo)
            med_container.add_widget(progress_container)

            meds_box.add_widget(med_container)

    def show_empty_state(self, container):
        """Muestra un mensaje cuando no hay medicamentos"""
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel
        from kivymd.uix.card import MDCard
        from kivy.uix.image import Image
        
        # Contenedor principal del mensaje
        empty_container = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(220),  # Altura reducida sin icono
            spacing=dp(20),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint_x=1
        )
        
        # Card del mensaje
        message_card = MDCard(
            orientation='vertical',
            size_hint_y=None,
            height=dp(180),  # Altura reducida sin icono
            padding=[dp(30), dp(20), dp(30), dp(20)],
            spacing=dp(15),  # Espaciado reducido
            md_bg_color=(0.98, 0.98, 0.98, 1),
            radius=[dp(20), dp(20), dp(20), dp(20)],
            elevation=2,
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint_x=0.9
        )
        
        # Espaciador para el icono (removido)
        icon_container = MDBoxLayout(
            size_hint_y=None,
            height=dp(20),  # Altura reducida
            pos_hint={'center_x': 0.5}
        )
        
        # Título del mensaje
        title_label = MDLabel(
            text="No hay medicamentos",
            theme_text_color="Custom",
            text_color=(0.3, 0.3, 0.3, 1),
            font_size="24sp",
            bold=True,
            halign="center",
            size_hint_y=None,
            height=dp(35)
        )
        
        # Mensaje descriptivo
        message_label = MDLabel(
            text="Cuando agregues un medicamento\nse mostrará aquí",
            theme_text_color="Custom",
            text_color=(0.5, 0.5, 0.5, 1),
            font_size="16sp",
            halign="center",
            size_hint_y=None,
            height=dp(50)
        )
        
        # Instrucción
        instruction_label = MDLabel(
            text="Ve a la pestaña 'Agregar' para comenzar",
            theme_text_color="Custom",
            text_color=(0.2, 0.6, 0.9, 1),
            font_size="14sp",
            bold=True,
            halign="center",
            size_hint_y=None,
            height=dp(25)
        )
        
        # Agregar elementos al card
        message_card.add_widget(icon_container)
        message_card.add_widget(title_label)
        message_card.add_widget(message_label)
        message_card.add_widget(instruction_label)
        
        # Agregar el card al contenedor
        empty_container.add_widget(message_card)
        
        # Agregar al contenedor principal
        container.add_widget(empty_container)

    def toggle_medication_details(self, medication):
        """Alterna la vista expandida de un medicamento"""
        medication['expanded'] = not medication.get('expanded', False)
        self.update_meds_list()

    def show_info_dialog(self, text):
        if self.dialog:
            self.dialog.dismiss()

        self.dialog = MDDialog(
            MDDialogHeadlineText(text="Aviso"),
            MDDialogSupportingText(text=text),
            MDButton(
                style="filled",
                on_release=lambda x: self.dialog.dismiss(),
                children=[
                    MDButtonIcon(icon="check"),
                    MDButtonText(text="OK")
                ]
            ),
        )
        self.dialog.open()

    def on_text_fields_change(self, *args):
        add_screen = self.root.ids.screen_manager.get_screen("Agregar")
        name = self.selected_medication
        time = add_screen.ids.med_time.text
        grams = add_screen.ids.med_grm.text
        days = add_screen.ids.med_days.text
        hours = add_screen.ids.med_hours.text
        add_screen.ids.save_button.disabled = not (name and time.strip() and grams.strip() and days.strip() and hours.strip())



    def on_start(self):
        # Inicializar y cargar DB
        self.init_db()
        self.load_medicines_from_db()

        Clock.schedule_interval(self.check_reminders, 60)

        # Mostrar estado vacío o lista
        self.update_meds_list()

        add_screen = self.root.ids.screen_manager.get_screen("Agregar")
        add_screen.ids.med_name.bind(text=self.on_text_fields_change)
        add_screen.ids.med_time.bind(text=self.on_text_fields_change)
        add_screen.ids.med_grm.bind(text=self.on_text_fields_change)
        add_screen.ids.med_days.bind(text=self.on_text_fields_change)
        add_screen.ids.med_hours.bind(text=self.on_text_fields_change)

    def check_reminders(self, dt):
        now = datetime.now().strftime("%H:%M")
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        for med in self.medicines:
            # Verificar si es hora de tomar el medicamento (incluyendo retrasos)
            current_time = med.get('current_alert_time', med['time'])
            if current_time == now:
                # Verificar si no está completado
                if not med.get('completed', False):
                    # Verificar si ya se notificó para este tiempo específico
                    last_notification_time = med.get('last_notification_time')
                    if last_notification_time != current_time:
                        if self.dialog:
                            self.dialog.dismiss()

                        def marcar_tomado(*args):
                            med['taken'] = True
                            med['taken_doses'] = min(med.get('taken_doses', 0) + 1, med.get('total_doses', 0))
                            
                            # Verificar si se completaron todas las dosis
                            if med['taken_doses'] >= med.get('total_doses', 0):
                                med['completed'] = True
                            
                            # Marcar como notificado para este tiempo específico
                            med['last_notification_time'] = current_time
                            
                            # Resetear el tiempo de alerta al original
                            med['current_alert_time'] = med['time']
                            
                            # Resetear el estado taken para la próxima dosis
                            med['taken'] = False
                            
                            # Persistir cambios
                            self.update_medicine_db(med)

                            self.update_meds_list()
                            self.dialog.dismiss()

                        # Función para retrasar notificación
                        def retrasar_notificacion(*args):
                            self.dialog.dismiss()
                            # Calcular nueva hora sumando 5 minutos
                            current_alert_time = med.get('current_alert_time', med['time'])
                            current_dt = datetime.strptime(current_alert_time, "%H:%M")
                            new_time = current_dt + timedelta(minutes=5)
                            new_time_str = new_time.strftime("%H:%M")
                            
                            # Marcar la notificación actual como enviada para evitar duplicados
                            med['last_notification_time'] = current_time
                            
                            # Actualizar el tiempo de alerta del medicamento
                            med['current_alert_time'] = new_time_str
                            
                            # Persistir cambios
                            self.update_medicine_db(med)

                            # Actualizar la lista de medicamentos para mostrar el nuevo tiempo
                            self.update_meds_list()
                            
                            # Programar nueva verificación en 5 minutos
                            Clock.schedule_once(lambda dt: self.check_reminders(dt), 300)
                        
                        # Crear el diálogo con diseño mejorado
                        delay_text = ""
                        if med.get('current_alert_time', med['time']) != med['time']:
                            delay_text = " (Retrasado)"
                        
                        # Crear el diálogo con el contenido personalizado usando el método correcto
                        self.dialog = MDDialog(
                            MDDialogHeadlineText(
                                text="¡Es hora de tu medicamento!",
                                halign="center",
                                theme_text_color="Custom",
                                text_color=(0.1, 0.3, 0.6, 1),
                                font_size="20sp",
                                bold=True
                            ),
                            MDDialogSupportingText(
                                text=f"💊 {med['name']} ({med['grams']}g)\n\n📅 Dosis: {med.get('taken_doses', 0) + 1}/{med.get('total_doses', 0)}\n\n🕐 Hora: {current_time}{delay_text}",
                                halign="center",
                                theme_text_color="Custom",
                                text_color=(0.4, 0.4, 0.4, 1),
                                font_size="16sp"
                            ),
                            MDDialogButtonContainer(
                                MDButton(
                                    MDButtonText(
                                        text="⏰ Retrasar 5 min",
                                        theme_text_color="Custom",
                                        text_color=(0.6, 0.6, 0.6, 1),
                                        font_size="14sp"
                                    ),
                                    style="outlined",
                                    line_color=(0.6, 0.6, 0.6, 1),
                                    on_release=retrasar_notificacion
                                ),
                                MDButton(
                                    MDButtonText(
                                        text="✓ Ya lo tomé",
                                        theme_text_color="Custom",
                                        text_color=(1, 1, 1, 1),
                                        font_size="14sp",
                                        bold=True
                                    ),
                                    style="filled",
                                    md_bg_color=(0.2, 0.7, 0.2, 1),
                                    on_release=marcar_tomado
                                ),
                                spacing="16dp"
                            ),
                            size_hint=(0.85, None),
                            height=dp(280),
                            radius=[dp(20), dp(20), dp(20), dp(20)],
                            elevation=8
                        )
                        self.dialog.open()
                        
                        # Marcar como notificado para este tiempo específico
                        med['last_notification_time'] = current_time
                        break  # Solo mostrar una notificación a la vez



if __name__ == "__main__":
    MedicineApp().run()
