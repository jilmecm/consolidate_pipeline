```mermaid
graph LR
    %% Definición de subgrafos y nodos
    
    subgraph DATA_INGESTION [DATA INGESTION AWS S3]
        S3[(AWS S3 Bucket)] 
        RP[📁 RAW Data Atlone]
        RC[📁 RAW Data SportsBar]
        S3 --> RP
        S3 --> RC
    end

    subgraph COMPUTATION [COMPUTATION ENGINE]
        Engine[🐍 Python + ✨ PySpark]
    end

    subgraph DATABRICKS_PLATFORM [DATABRICKS PLATFORM - 🛡️ Unity Catalog & 🔺 Delta Lake]
        
        subgraph BRONZE_LAYER [🥉 BRONZE LAYER]
            BP[(Bronze Parent)]
            BC[(Bronze Child)]
        end
        
        subgraph SILVER_LAYER [🥈 SILVER LAYER]
            SP[(Silver Parent)]
            SC[(Silver Child)]
            MU[⚙️ MERGE Upsert: Dummy Record ID 999999]
            %% Conexión invisible para mantener el cuadro del Merge debajo del Silver Child
            SC -.- MU 
        end
        
        subgraph GOLD_LAYER [🥇 GOLD LAYER]
            GC[(Gold Catalog)]
            
            subgraph STAR_SCHEMA [Star Schema]
                direction TB
                DC[Dim_Customer] --- F[Fact_Orders]
                DP[Dim_Product] --- F
                DD[Dim_Date] --- F
                DGP[Dim_Gross_Price] --- F
            end
        end
    end

    subgraph SERVING_LAYER [SERVING LAYER BI & INSIGHTS]
        BI[📊 Databricks Lakeview Dashboards]
    end

    %% Conexiones principales del flujo de datos
    RP --> Engine
    RC --> Engine
    
    Engine --> BP
    Engine --> BC
    
    BP --> SP
    BC --> SC
    
    SP --> GC
    SC --> GC
    
    GC --> BI

    %% Estilos de colores (Inspirados en tu diseño)
    style BRONZE_LAYER fill:#FDE1D3,stroke:#D88C70,stroke-width:2px
    style SILVER_LAYER fill:#DDEBF7,stroke:#9CA3AF,stroke-width:2px
    style GOLD_LAYER fill:#FFF2CC,stroke:#D6B656,stroke-width:2px
    style DATA_INGESTION fill:#F9FBFD,stroke:#9CA3AF,stroke-width:2px
    style SERVING_LAYER fill:#F9FBFD,stroke:#9CA3AF,stroke-width:2px
    style DATABRICKS_PLATFORM fill:#F0F4F8,stroke:#3D85C6,stroke-width:2px
    style STAR_SCHEMA fill:#E8F0FE,stroke:#4285F4,stroke-width:1px
    
    %% Colores específicos de los cilindros y nodos
    style GC fill:#FFD966,stroke:#B38F00,stroke-width:2px
    style MU fill:#FFE699,stroke:#D6B656,stroke-width:2px
    style BP fill:#E6B8AF,stroke:#A64D79,stroke-width:1px
    style BC fill:#E6B8AF,stroke:#A64D79,stroke-width:1px
    style SP fill:#CFE2F3,stroke:#3D85C6,stroke-width:1px
    style SC fill:#CFE2F3,stroke:#3D85C6,stroke-width:1px
    style F fill:#9FC5E8,stroke:#0B5394,stroke-width:1px
    style DC fill:#FFFFFF,stroke:#B7B7B7,stroke-width:1px
    style DP fill:#FFFFFF,stroke:#B7B7B7,stroke-width:1px
    style DD fill:#FFFFFF,stroke:#B7B7B7,stroke-width:1px
    style DGP fill:#FFFFFF,stroke:#B7B7B7,stroke-width:1px
```
# 🚀 Atlone Enterprise: Data Consolidation Pipeline

## 📊 Resumen Ejecutivo
Este proyecto es una solución integral de Ingeniería de Datos diseñada para resolver un problema clásico de fusiones y adquisiciones corporativas: la **consolidación de datos**. 

El objetivo principal fue unificar las ventas y métricas operativas de la empresa matriz (**Atlone Enterprise**) con su nueva subsidiaria (**SportsBar**), integrando dos fuentes de datos dispares en una única fuente de la verdad (Single Source of Truth) para la toma de decisiones gerenciales, asegurando la integridad referencial y automatizando la actualización de tableros de Business Intelligence.

---

## 🏗️ Arquitectura de Datos (Medallion Architecture)

El pipeline fue construido utilizando el estándar de la industria **Medallion Architecture** dentro del ecosistema de Databricks, garantizando escalabilidad y calidad de datos.

![Diagrama de Arquitectur](images/medallion.jpg)

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
## 🛠️ Tecnologías y Herramientas Utilizadas

El pipeline fue diseñado e implementado utilizando un *stack* moderno de ingeniería de datos, enfocado en el rendimiento computacional, transacciones ACID y un estricto gobierno de la información:

* **Lenguajes & Frameworks:** `Python` | `Apache Spark (PySpark)` | `SQL`
* **Infraestructura & Plataforma:** `Databricks Data Intelligence Platform` | `AWS S3` (Ingesta Raw)
* **Arquitectura & Almacenamiento:** `Medallion Architecture` (Bronze, Silver, Gold) | `Delta Lake`
* **Gobierno de Datos & Orquestación:** `Unity Catalog` | `Databricks Workflows`
* **Técnicas de Ingeniería:** Procesamiento en Paralelo | `MERGE` Upserts | Integridad Referencial (Dummy Records)
* **Modelado & Visualización:** `Data Modeling (Star Schema)` | `Databricks Lakeview Dashboards`
