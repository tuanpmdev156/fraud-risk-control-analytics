-- Return records have invalid fraud rate
SELECT
    transaction_date,
    card_network,
    fraud_rate
FROM {{ ref('mart_risk_summary') }}
WHERE fraud_rate < 0 OR fraud_rate > 100