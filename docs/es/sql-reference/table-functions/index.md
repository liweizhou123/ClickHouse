---
machine_translated: true
machine_translated_rev: 3e185d24c9fe772c7cf03d5475247fb829a21dfa
toc_folder_title: Table Functions
toc_priority: 34
toc_title: "Implantaci\xF3n"
---

# Funciones De Tabla {#table-functions}

Las funciones de tabla son métodos para construir tablas.

Puede usar funciones de tabla en:

-   [FROM](../statements/select.md#select-from) cláusula de la `SELECT` consulta.

        The method for creating a temporary table that is available only in the current query. The table is deleted when the query finishes.

-   [CREAR TABLA COMO \<table\_function()\>](../statements/create.md#create-table-query) consulta.

        It's one of the methods of creating a table.

!!! warning "Advertencia"
    No puede usar funciones de tabla si el [Método de codificación de datos:](../../operations/settings/permissions-for-queries.md#settings_allow_ddl) la configuración está deshabilitada.

| Función              | Descripci                                                                                                                              |
|----------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| [file](file.md)      | Crea un [File](../../engines/table-engines/special/file.md)-mesa del motor.                                                            |
| [fusionar](merge.md) | Crea un [Fusionar](../../engines/table-engines/special/merge.md)-mesa del motor.                                                       |
| [numero](numbers.md) | Crea una tabla con una sola columna llena de números enteros.                                                                          |
| [remoto](remote.md)  | Le permite acceder a servidores remotos sin crear un [Distribuido](../../engines/table-engines/special/distributed.md)-mesa del motor. |
| [URL](url.md)        | Crea un [URL](../../engines/table-engines/special/url.md)-mesa del motor.                                                              |
| [mysql](mysql.md)    | Crea un [MySQL](../../engines/table-engines/integrations/mysql.md)-mesa del motor.                                                     |
| [jdbc](jdbc.md)      | Crea un [JDBC](../../engines/table-engines/integrations/jdbc.md)-mesa del motor.                                                       |
| [Nosotros](odbc.md)  | Crea un [ODBC](../../engines/table-engines/integrations/odbc.md)-mesa del motor.                                                       |
| [Hdfs](hdfs.md)      | Crea un [HDFS](../../engines/table-engines/integrations/hdfs.md)-mesa del motor.                                                       |

[Artículo Original](https://clickhouse.tech/docs/en/query_language/table_functions/) <!--hide-->
