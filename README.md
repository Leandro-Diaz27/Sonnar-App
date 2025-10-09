# 💊 Sonnar, tu sistema de Recordatorios de Medicación

Este proyecto permite gestionar medicamentos, recordatorios y acciones asociadas, facilitando el seguimiento de tratamientos y la trazabilidad de dosis en tiempo real.

---

## 📦 Estructura del Proyecto

- `/diagrams/`  
  Diagramas ER y relacionales en formato `.md` y visual (.png)

- `/sql/`  
  Scripts de creación de base de datos, índices y restricciones

- `/main.py/`  
  Codigo principal de la aplicación junto con la logica

- `/medicamentos.kv`  
   Estilos principales de la aplicación

- `/medicamentos.db/`  
   Base de datos de la aplicación

---

## 🧠 Funcionalidades Clave

- Registro de medicamentos
- Generación automática de recordatorios según frecuencia y horario
- Registro de acciones (`Tomar`, `Posponer`) con trazabilidad completa
- Cálculo de dosis restantes y estado de cumplimiento
- Alertas en tiempo real y control de notificaciones

---

## 🗃️ Modelo Relacional

El sistema se compone de las siguientes tablas:

| Tabla               | Descripción                                      |
|---------------------|--------------------------------------------------|
| `Medicamento`       | Nombre, horario, cantidad, días, intervalo       |
| `Recordatorio`      | Fecha, hora de alerta, repetición, días          |
| `Accion_Recordatorio` | Tipo de acción, fecha/hora, dosis y días restantes |

---
