SELECT
    SUM(total_transaction) AS total_transactions,
    ROUND(SAFE_DIVIDE(SUM(fraud_transaction), SUM(total_transaction)), 4) AS fraud_rate_pct,
    SUM(fraud_transaction) AS total_fraud_transactions,
    ROUND(SUM(total_fraud_amount) / 1000000, 2) AS total_fraud_amount,
    ROUND(SUM(total_amount) / 1000000, 2) AS total_amount
FROM production.fraud_risk_summary

