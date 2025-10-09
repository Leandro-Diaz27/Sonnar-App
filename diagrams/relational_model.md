# 📘 Modelo Relacional: Sistema de Recordatorios de Medicación

Este documento describe la estructura relacional del sistema, incluyendo tablas, columnas, tipos de datos, claves, relaciones y restricciones.

---

## 🧑‍⚕️ Tabla: Usuario

- **PK**: `ID_Usuario` (INT, NOT NULL, AUTO_INCREMENT)
- **Columnas**:
  - `Nombre` (VARCHAR(100), NOT NULL)
  - `Correo` (VARCHAR(150), NOT NULL, UNIQUE)

---

## 💊 Tabla: Medicamento

- **PK**: `ID_Medicamento` (INT, NOT NULL, AUTO_INCREMENT)
- **FK**: `ID_Usuario` → Usuario(`ID_Usuario`)
- **Columnas**:
  - `Nombre` (VARCHAR(100), NOT NULL)
  - `Hora` (TIME, NOT NULL)
  - `Cantidad` (INT, NOT NULL, CHECK > 0)
  - `Dias` (VARCHAR(50), NOT NULL)
  - `Intervalo_horas` (INT, NULL)

- **Índices**:
  - `idx_usuario_medicamento` (`ID_Usuario`)
  - `UNIQUE(Nombre, ID_Usuario)`

---

## ⏰ Tabla: Recordatorio

- **PK**: `ID_Recordatorio` (INT, NOT NULL, AUTO_INCREMENT)
- **FK**: `ID_Usuario` → Usuario(`ID_Usuario`)
- **Columnas**:
  - `Hora_Alerta` (TIME, NOT NULL)
  - `Fecha` (DATE, NOT NULL)
  - `RepetirCadaHoras` (INT, NULL)
  - `Dias` (VARCHAR(50), NOT NULL)
  - `Intervalo_horas` (INT, NULL)

- **Índices**:
  - `idx_usuario_recordatorio` (`ID_Usuario`)

---

## ✅ Tabla: Accion_Recordatorio

- **PK**: `ID_Accion` (INT, NOT NULL, AUTO_INCREMENT)
- **FK**: `ID_Recordatorio` → Recordatorio(`ID_Recordatorio`)
- **Columnas**:
  - `TipoAccion` (ENUM('Tomar', 'Posponer'), NOT NULL)
  - `FechaHora` (DATETIME, NOT NULL)
  - `DosisRestantes` (INT, NULL)
  - `DiasRestantes` (INT, NULL)

- **Índices**:
  - `idx_recordatorio_accion` (`ID_Recordatorio`)

---

## 🔗 Relaciones y Cardinalidades

- `Usuario` 1 — n `Medicamento`
- `Usuario` 1 — n `Recordatorio`
- `Recordatorio` 1 — n `Accion_Recordatorio`

---

## 🛡️ Recomendaciones adicionales

- Agregar `FechaCreacion` y `FechaModificacion` en todas las tablas para trazabilidad.
- Implementar `ON DELETE CASCADE` en las FK si se desea limpieza automática.
- Validar `Correo` con formato estándar en capa de aplicación.

---

