SELECT
    transaction_date,
    SUM(total_transaction) AS total_transactions,
    SUM(fraud_transaction) AS total_fraud_transactions,
    ROUND(SAFE_DIVIDE(SUM(fraud_transaction), SUM(total_transaction)), 4) AS fraud_rate,
    ROUND(SUM(total_fraud_amount), 2) AS fraud_loss
FROM production.fraud_risk_summary
GROUP BY transaction_date
ORDER BY transaction_date