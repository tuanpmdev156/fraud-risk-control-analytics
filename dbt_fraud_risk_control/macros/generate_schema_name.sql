-- Standardize schema name to 'staging' & 'production' to match with Bigquery
-- By default: dbt generates dbt_staging, dbt_production

{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- set default_schema = target.schema -%}
    {%- if custom_schema_name is none -%}
        {{default_schema}}
    {%- else -%}
        {{ custom_schema_name | trim}}
    {%- endif -%}
{%- endmacro -%}