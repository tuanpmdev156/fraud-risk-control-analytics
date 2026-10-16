{{
    config(
        materialized='table',
        partition_by={
            "field": "transaction_date",
            "data_type": "date",
            "granularity": "day"
        },
        cluster_by=["product_code", "card_network", "is_fraud"]
    )
}}

WITH transactions AS (
    SELECT * FROM {{ ref('stg_transaction') }}
),
identities AS (
    SELECT * FROM {{ ref('stg_identity') }}
)

SELECT
    -- Primary Key & Label
    t.transaction_id,
    t.is_fraud,
    -- Timestamps & Temporal Dimensions
    t.transaction_timestamp,
    t.transaction_date,
    t.transaction_hour,
    t.day_of_week,
    -- Transaction Detail
    t.transaction_amount,
    t.amount_level,
    t.product_code,
    -- Card Details
    t.bank_code,
    t.branch,
    t.card_network,
    t.card_type,
    -- Geographic & Contact Details
    t.billing_region,
    t.billing_country,
    t.distance,
    t.p_emaildomain,
    t.r_emaildomain,
    -- Device & Identity Attributes
    COALESCE(i.device_type, 'unknown') AS device_type,
    COALESCE(i.device_info, 'unknown') AS device_info,
    COALESCE(i.os_version, 'unknown') AS os_version,
    COALESCE(i.browser, 'unknown') AS browser,
    CASE WHEN i.transaction_id IS NOT NULL THEN 1 ELSE 0 END AS has_identity_info
FROM transactions AS t
LEFT JOIN identities AS i
    ON t.transaction_id = i.transaction_id