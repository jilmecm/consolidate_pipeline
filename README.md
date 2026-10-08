# 🚀 Atlone Enterprise: Data Consolidation Pipeline

## 📊 Resumen Ejecutivo
Este proyecto es una solución integral de Ingeniería de Datos diseñada para resolver un problema clásico de fusiones y adquisiciones corporativas: la **consolidación de datos**. 

El objetivo principal fue unificar las ventas y métricas operativas de la empresa matriz (**Atlone Enterprise**) con su nueva subsidiaria (**SportsBar**), integrando dos fuentes de datos dispares en una única fuente de la verdad (Single Source of Truth) para la toma de decisiones gerenciales, asegurando la integridad referencial y automatizando la actualización de tableros de Business Intelligence.

---

## 🏗️ Arquitectura de Datos (Medallion Architecture)

El pipeline fue construido utilizando el estándar de la industria **Medallion Architecture** dentro del ecosistema de Databricks, garantizando escalabilidad y calidad de datos.

```mermaid
graph LR
    subgraph AWS Cloud
        S3[(S3: Raw Data)]
    end

    subgraph Databricks [Databricks Data Intelligence Platform]
        direction LR
        subgraph Medallion Architecture
            B[🥉 Bronze Layer] --> S1[🥈 Silver: Atlone]
            B --> S2[🥈 Silver: SportsBar]
            
            S1 --> G[🥇 Gold Layer]
            S2 -->|Merge & Dummy Record| G
        end
    end

    subgraph Serving Layer
        BI[📊 Databricks Dashboard]
    end

    S3 -->|Lakeflow / Auto Loader| B
    G -->|Star Schema| BI

    style S3 fill:#FF9900,stroke:#232F3E,stroke-width:2px,color:white
    style B fill:#CD7F32,stroke:#333,stroke-width:2px,color:white
    style S1 fill:#C0C0C0,stroke:#333,stroke-width:2px,color:black
    style S2 fill:#C0C0C0,stroke:#333,stroke-width:2px,color:black
    style G fill:#FFD700,stroke:#333,stroke-width:2px,color:black
    style BI fill:#FF3621,stroke:#333,stroke-width:2px,color:white
```
> **[Insertar imagen: Diagrama de Arquitectura - Crear en draw.io o similar]**
*(Nota: Aquí irá el diagrama visual de cómo fluyen los datos desde los CSV/Sistemas origen hasta el Dashboard).*

### Estructura del Catálogo (Unity Catalog)
Los datos se organizaron de forma lógica y segura utilizando catálogos y esquemas separados:
*   🥉 **Capa Bronze (`bronze_parent` / `bronze_child`):** Datos crudos y sin procesar, manteniendo la inmutabilidad histórica.
*   🥈 **Capa Silver (`silver_parent` / `silver_child`):** Datos limpios, filtrados y estandarizados. Aquí se manejó la imputación de valores nulos y la corrección de anomalías en los IDs de clientes (generación de *Dummy Records*).
*   🥇 **Capa Gold (`gold`):** Modelo dimensional consolidado (Star Schema) listo para el consumo de BI.

![Estrutura catálogo](images/Estructura_del_Catálogo.png)

---

## ⚙️ Orquestación y Flujo del Pipeline (Data Flow)

Para optimizar los tiempos de cómputo y los costos en la nube, el flujo de trabajo fue diseñado con **procesamiento paralelo** para las dimensiones independientes, convergiendo en nodos secuenciales para las tablas de hechos y la consolidación final.

![Graph - Pipelines](images/Graph_Pipelines.png)

*   **Fase 1 (Extracción y Limpieza Paralela):** Procesamiento simultáneo de clientes, productos y precios tanto para la empresa matriz como para la subsidiaria.
*   **Fase 2 (Validación de Hechos):** Carga incremental de las órdenes de venta (`fact_orders`) asegurando que las dimensiones maestras ya estén disponibles.
*   **Fase 3 (Consolidación Gold):** Unificación de ambas empresas mediante operaciones `MERGE` (Upserts) en tablas Delta, evitando duplicidades.
*   **Fase 4 (BI Automático):** Tarea final automatizada para refrescar el Dashboard (`9_refresh_dashboard`) solo cuando los datos superaron todas las validaciones.

![Timeline - Pipeline](images/Timeline_Pipeline.png)

---

## 🔗 Modelado de Datos y Linaje (Data Lineage)

El modelo de datos final expuesto a la capa de negocios es un **Modelo en Estrella (Star Schema)** compuesto por tres dimensiones consolidadas (`dim_customers`, `dim_products`, `dim_gross_price`) y una tabla de hechos central (`4_fact_orders`).

Se implementó un rastreo estricto de linaje de datos para garantizar la observabilidad y permitir auditorías rápidas sobre el origen de cualquier métrica.

![Data Lineage Graph](images/Data_Lineage_Graph.png)

### 🛠️ Desafío Técnico Destacado: Integridad Referencial
Durante la ingesta, la subsidiaria presentaba ventas con IDs de clientes nulos o inválidos. Para evitar la pérdida de facturación en el cálculo del *Total Revenue* del Dashboard, se implementó la inyección automatizada de un **Registro Ficticio (Dummy Record: 999999)** en la capa Silver. Esto garantizó una relación perfecta de 1 a N (Modelo Estrella) sin valores huérfanos, etiquetando los errores para visibilidad del equipo de calidad de datos.

---

## 🛡️ Observabilidad y Delta Lake (Time Travel)

Todas las tablas fueron creadas bajo el formato **Delta Lake**, aprovechando el registro de transacciones (Transaction Log). Esto permite:
*   Transacciones ACID confiables.
*   Control de versiones de los datos (*Time Travel*).
*   Monitoreo de operaciones `MERGE` y `CREATE OR REPLACE TABLE`.

![History data](images/History_data.png)

---

## 📈 Business Intelligence & Resultados

El pipeline culmina en un panel de control automatizado que permite a los *stakeholders* filtrar la información a nivel global (Consolidado) o realizar *drill-down* por empresa origen (Atlone vs. SportsBar). 

**Métricas Clave (KPIs) Analizadas:**
*   Ingresos Totales (Total Revenue).
*   Unidades Vendidas.
*   Clientes Únicos.
*   Distribución de ingresos por canal y tendencia mensual.

[![Vista previa del Dashboard](images/atlone_enterprise_images.png)](3_dashboards/atlone_enterprise.pdf)

> [📥 Haz clic aquí para ver el Dashboard completo con todos los KPIs en formato PDF](3_dashboards/atlone_enterprise.pdf)

---
**Tecnologías Utilizadas:**
`Apache Spark (PySpark)` | `Databricks (Workflows, Unity Catalog)` | `Delta Lake` | `SQL` | `Data Modeling (Star Schema)` | `Business Intelligence`
