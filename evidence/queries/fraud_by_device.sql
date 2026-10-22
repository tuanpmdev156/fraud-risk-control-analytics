SELECT
    COALESCE(NULLIF(device_type, ''), 'unknown') AS device_type,
    SUM(total_transaction) AS total_txns,
    SUM(fraud_transaction) AS fraud_txns,
    ROUND(SAFE_DIVIDE(SUM(fraud_transaction), SUM(total_transaction)), 4) AS fraud_rate_pct
FROM production.fraud_risk_summary
GROUP BY device_type
ORDER BY fraud_rate_pct DESC

