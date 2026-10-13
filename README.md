# Proyecto Backend - Taller Mecánico

Proyecto orientado al desarrollo de un sistema backend para apoyar la gestión de un taller mecánico.

## Problema a trabajar

Los talleres mecánicos pequeños suelen registrar la información de sus clientes, vehículos, órdenes de trabajo y reparaciones de forma manual o poco organizada. Esto dificulta el seguimiento de los trabajos realizados, el estado de las reparaciones y el historial de cada vehículo. El proyecto busca centralizar esta información en un sistema que permita gestionarla de manera más ordenada y eficiente.

## Integrantes

| Nombre |
| :--- |
| **Carlos Nahuelcoy** |
| **Gonzalo Albornoz** |
| **Rodrigo Sevilla** |
| **Matias Salinas** |

## Módulos del sistema

El sistema se divide en cuatro módulos principales:

- Clientes
- Vehículos
- Órdenes de Trabajo
- Reparaciones

Cada módulo se encarga de una parte específica del funcionamiento del sistema y se relaciona con los demás para mantener la información organizada.

## Estructura del proyecto

El proyecto está organizado por capas para separar las distintas responsabilidades del sistema.

```text
src/proyectobackend/
├── database/
├── domain/
├── models/
├── repositories/
├── routers/
├── schemas/
├── services/
└── main.py
```

## Dependencias actuales

El proyecto utiliza actualmente las siguientes dependencias:

- Python >= 3.13
- FastAPI >= 0.141.1
- Pydantic >= 2.13.5
- SQLAlchemy >= 2.1.4
- Uvicorn >= 0.52.4

La gestión de dependencias y del entorno del proyecto se realiza mediante `uv`.