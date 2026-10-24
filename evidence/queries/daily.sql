SELECT
    transaction_date,
    SUM(total_transaction) AS total_transactions,
    SUM(fraud_transaction) AS fraud_transactions,
    ROUND(SAFE_DIVIDE(SUM(fraud_transaction), SUM(total_transaction)), 4) AS fraud_rate_pct,
    ROUND(SUM(total_amount), 2) AS total_amount,
    ROUND(SUM(total_fraud_amount), 2) AS total_fraud_amount,
FROM production.fraud_risk_summary
GROUP BY transaction_date
ORDER BY transaction_date