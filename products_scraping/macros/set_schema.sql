{% macro generate_schema_name(custom_schema_name, node) %}
    -- Ignora el schema por defecto de dbt y usa siempre 'catalog'
    {{ return("catalog") }}
{% endmacro %}