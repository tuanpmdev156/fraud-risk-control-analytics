SELECT
    product_code,
    SUM(total_transaction) AS total_transaction,
    SUM(fraud_transaction) AS fraud_transaction,
    ROUND(SAFE_DIVIDE(SUM(fraud_transaction), SUM(total_transaction)), 4) AS fraud_rate_pct,
    SUM(total_amount) AS total_amount,
    SUM(total_fraud_amount) AS total_fraud_amount,
FROM production.fraud_risk_summary
GROUP BY product_code
ORDER BY fraud_rate_pct DESC