-- Transformation of transaction table

WITH raw_trans AS (
    SELECT * FROM {{ source('raw','ext_transaction')}}
),

transformed_trans AS
(
    SELECT
        -- Primary Key & Label
        CAST(TransactionID AS INT64) AS transaction_id,
        CAST(isFraud AS INT64) AS is_fraud,

         -- Transaction Details
        CAST(TransactionAmt AS FLOAT64) AS transaction_amount,
        {{ classify_amount('CAST(TransactionAmt AS FLOAT64)') }} AS amount_level,
        CAST(ProductCD AS STRING) AS product_code,

        -- Card Details
        CAST(card1 AS INT64) AS bank_code,
        CAST(card2 AS FLOAT64) AS branch,
        LOWER(CAST(card4 AS STRING)) AS card_network,
        LOWER(CAST(card6 AS STRING)) AS card_type,

         -- Geographic & Contact Details
        CAST(addr1 AS FLOAT64) AS billing_region,
        CAST(addr2 AS FLOAT64) AS billing_country,
        CAST(dist1 AS FLOAT64) AS distance,
        LOWER(CAST(P_emaildomain AS STRING)) AS p_emaildomain,
        LOWER(CAST(R_emaildomain AS STRING)) AS r_emaildomain,

        -- Convert TransactionDT (seconds from 2017-12-01 00:00:00 UTC)
        TIMESTAMP_ADD(
            TIMESTAMP '2017-12-01 00:00:00 UTC',
            INTERVAL CAST(TransactionDT AS INT64) SECOND
        ) AS transaction_timestamp
    FROM raw_trans
)


SELECT
    transaction_id,
    transaction_timestamp,
    DATE(transaction_timestamp) AS transaction_date,
    EXTRACT(HOUR FROM transaction_timestamp) AS transaction_hour,
    EXTRACT(DAYOFWEEK FROM transaction_timestamp) AS day_of_week,
    is_fraud,
    transaction_amount,
    amount_level,
    product_code,
    bank_code,
    branch,
    card_network,
    card_type,
    billing_region,
    billing_country,
    distance,
    p_emaildomain,
    r_emaildomain
FROM transformed_trans
WHERE transaction_amount > 0 AND is_fraud IN (0, 1)
-- Deduplication TransactionID
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY transaction_id 
    ORDER BY transaction_timestamp DESC
) = 1