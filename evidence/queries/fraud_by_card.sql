SELECT
    COALESCE(NULLIF(card_network, ''), 'other') AS card_network,
    SUM(total_transaction) AS total_txns,
    SUM(fraud_transaction) AS fraud_txns,
    ROUND(SAFE_DIVIDE(SUM(fraud_transaction), SUM(total_transaction)), 4) AS fraud_rate_pct
FROM production.fraud_risk_summary
GROUP BY card_network
ORDER BY fraud_rate_pct DESC