
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
    *,
    CURRENT_TIMESTAMP() AS quarantined_at,
    CASE 
        WHEN transaction_amount <= 0 THEN 'invalid_transaction_amount'
        WHEN is_fraud NOT IN (0, 1) THEN 'invalid_fraud_flag'
        ELSE 'other'
    END AS quarantine_reason
FROM transformed_trans
WHERE transaction_amount <= 0 OR is_fraud NOT IN (0, 1)