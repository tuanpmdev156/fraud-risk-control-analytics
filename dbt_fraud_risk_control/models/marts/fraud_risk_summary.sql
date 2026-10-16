-- Pre-aggregated data ready for dashboard, analysis
{{
    config(
        materialized='table',
        partition_by={
            "field": "transaction_date",
            "data_type": "date",
            "granularity": "day"
        },
        cluster_by=["card_network", "product_code", "device_type"]
    )
}}

WITH fct_transactions AS (
    SELECT * FROM {{ ref('fct_transaction') }}
)

SELECT
    -- Dimensional grains
    transaction_date,
    COALESCE(card_network,'unknown') AS card_network,
    product_code,
    device_type,
    -- Transaction metrics
    COUNT(*) AS total_transaction,
    COUNTIF(is_fraud = 1) AS fraud_transaction,
    COUNTIF(is_fraud = 0) AS legit_transaction,
    -- Fraud rate (%)
    ROUND(SAFE_DIVIDE(COUNTIF(is_fraud = 1), COUNT(1)) * 100, 4) AS fraud_rate,
    -- Aggregated metrics
    ROUND(SUM(transaction_amount), 2) AS total_amount,
    ROUND(SUM(CASE WHEN is_fraud = 1 THEN transaction_amount ELSE 0 END), 2) AS total_fraud_amount,
    ROUND(AVG(transaction_amount), 2) AS avg_transaction_amount,
    ROUND(AVG(CASE WHEN is_fraud = 1 THEN transaction_amount ELSE NULL END), 2) AS avg_fraud_amount
FROM 
    fct_transactions
GROUP BY 
    transaction_date,
    card_network,
    product_code,
    device_type