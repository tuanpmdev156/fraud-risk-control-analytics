SELECT
    amount_level,
    COUNT(*) AS total_txns,
    COUNTIF(is_fraud = 1) AS fraud_txns,
    ROUND(SAFE_DIVIDE(COUNTIF(is_fraud = 1), COUNT(*)), 4) AS fraud_rate_pct,
    ROUND(SUM(transaction_amount), 2) AS total_amt,
    SUM(CASE WHEN is_fraud = 1 THEN transaction_amount ELSE 0 END) AS total_fraud_amount
FROM production.fct_transaction
GROUP BY amount_level
ORDER BY fraud_rate_pct DESC

