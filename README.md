# 📦 Sistema de Control de Inventario

Este proyecto consiste en el desarrollo de un sistema web para la gestión de inventarios, orientado a pequeños negocios. Permite administrar clientes, productos, ventas y pagos, además de generar reportes y visualizar estadísticas mediante un panel de control (dashboard).
El sistema fue desarrollado utilizando Python con el framework Flask, implementando una arquitectura modular basada en Blueprints y una base de datos SQLite.


## 🎯 Objetivo
Desarrollar un sistema que permita:
•	Controlar el inventario de productos
•	Gestionar clientes y sus deudas
•	Registrar ventas y pagos
•	Generar reportes en PDF
•	Visualizar estadísticas en tiempo real


---

### 🚀 Funcionalidades

👤 Clientes
•	Registro de clientes
•	Edición de información
•	Eliminación lógica
•	Control de deuda y pagos realizados


### 📦 Productos

* Registro de productos
* Control de stock actual
* ✅ Control de **stock mínimo**
* 🔴 Alertas visuales cuando el stock está bajo

### 🛒 Ventas

* Registro de ventas con múltiples productos
* Cálculo automático de:

  * Subtotal
  * IVA (12%)
  * Total
* Descuento automático de stock
* Aumento automático de deuda del cliente

### 💰 Pagos

* Registro de pagos por cliente
* Validaciones:

  * No pagar más de la deuda
  * No valores negativos
* Reducción automática de deuda

### ❌ Anulación

* Anular ventas → devuelve stock y reduce deuda
* Anular pagos → resta pago y devuelve deuda

### 📊 Dashboard

* Total de clientes
* Total de productos
* Total de ventas
* Deuda total
* 📈 Gráfica de ventas por día (Chart.js)

### 📄 Reportes

* Generación de PDF de clientes con deuda
* Descarga directa desde el sistema

### 🔐 Seguridad

* Sistema de login
* Protección de rutas
* Manejo de errores (404 y 500)

---
## 🗄️ Base de Datos
El sistema utiliza SQLite con las siguientes tablas:
•	clientes
•	productos
•	ventas
•	detalle_venta
•	pagos
•	usuarios
---

## 🛠 Tecnologías Utilizadas

* Python
* Flask
* SQLite
* HTML5
* Bootstrap
* JavaScript
* Chart.js
* ReportLab (PDF)

---

## 🧪 Usuario de Prueba

Usuario por defecto:

```
Usuario: admin
Contraseña: 1234
```

## 🌐 Acceso

Abrir en navegador:

```
http://127.0.0.1:5000
```

---

## 📁 Estructura del Proyecto

```
PROYECTO/
│── app.py
│── database.py
│── inventario.db
│
├── routes/
│   ├── clientes.py
│   ├── productos.py
│   ├── ventas.py
│   └── pagos.py
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── clientes/
│   ├── productos/
│   ├── ventas/
│   ├── pagos/
│   └── errores/
```

---

## 📌 Características Destacadas

* ✔ Sistema completo CRUD
* ✔ Validaciones en backend
* ✔ Manejo de errores
* ✔ Control financiero (deuda/pagos)
* ✔ Control de inventario en tiempo real
* ✔ Generación de reportes PDF
* ✔ Dashboard interactivo

---

## 👩‍💻 Autor

Desarrollado por:
**Angie Bayas**

---

## 📄 Licencia

Uso académico.

