---
title: Fraud Risk Analytics Dashboard
---

## Executive Scorecards

<BigValue data={kpi_overview} value=total_transactions title="Transactions Analyzed" fmt="num0" />
<BigValue data={kpi_overview} value=fraud_rate_pct title="Overall Fraud Rate" fmt="pct2" />
<BigValue data={kpi_overview} value=total_fraud_amount title="Fraud Exposure ($M)" fmt="usd1" />
<BigValue data={top_risk_product} value=product title="Highest Risk Product" />

---

## Daily Fraud Activity

> Transaction volume and fraud count across the observation period.

<LineChart
    data={daily}
    x=transaction_date
    y={['total_transactions', 'fraud_transactions']}
    yAxisTitle="Total Transactions"
    yFmt="num0"
    colorPalette={['#4A7FB5', '#C23D2E']}
/>

---

## Fraud Distribution by Category

> Fraud rate across product codes and card networks.

<Grid cols=2>
    <BarChart
        data={fraud_by_product}
        x=product_code
        y=fraud_rate_pct
        swapXY=true
        title="BY PRODUCT CODE"
        yFmt="pct1"
        fillColor="#4A7FB5"
    />
    <BarChart
        data={fraud_by_card}
        x=card_network
        y=fraud_rate_pct
        swapXY=true
        title="BY CARD NETWORK"
        yFmt="pct1"
        fillColor="#C23D2E"
    />
</Grid>

---

## Transaction Profile & Breakdown

> Fraud patterns by client device type and product-level risk breakdown.

<Grid cols=2>
    <BarChart
        data={fraud_by_device}
        x=device_type
        y=fraud_rate_pct
        swapXY=true
        title="BY DEVICE TYPE"
        yFmt="pct2"
        fillColor="#2B6B5E"
    />
    <DataTable data={fraud_by_product} title="PRODUCT CODE SUMMARY">
        <Column id=product_code title="Product" />
        <Column id=total_transaction title="Total Txns" fmt="num0" />
        <Column id=fraud_transaction title="Fraud Txns" fmt="num0" />
        <Column id=fraud_rate_pct title="Fraud Rate" fmt="pct2" />
        <Column id=total_fraud_amount title="Fraud Amt" fmt="usd2" />
    </DataTable>
</Grid>

---

## Risk by Transaction Size

> Fraud rate across amount buckets — higher-value transactions show elevated risk.

<BarChart
    data={amount_buckets}
    x=amount_level
    y=fraud_rate_pct
    yFmt="pct2"
    fillColor="#D4890A"
    subtitle="Amount buckets: micro(<$50), low($50–$100), medium($100–$500), high($500–$2,000), critical(>$2,000)"
/>

---

## Data Sources & Inspection

### Daily Trend

<DataTable data={daily}>
    <Column id=transaction_date title="Transaction Date" />
    <Column id=total_transactions title="Total Txns" fmt="num0" />
    <Column id=fraud_transactions title="Fraud Txns" fmt="num0" />
    <Column id=fraud_rate_pct title="Fraud Rate" fmt="pct2" />
    <Column id=total_amount title="Total Amt" fmt="usd2" />
    <Column id=total_fraud_amount title="Fraud Amt" fmt="usd2" />
</DataTable>

### By Card Network

<DataTable data={fraud_by_card}>
    <Column id=card_network title="Card Network" />
    <Column id=total_txns title="Total Txns" fmt="num0" />
    <Column id=fraud_txns title="Fraud Txns" fmt="num0" />
    <Column id=fraud_rate_pct title="Fraud Rate" fmt="pct2" />
    <Column id=total_fraud_amount title="Fraud Amt" fmt="usd2" />
</DataTable>

### By Device Type

<DataTable data={fraud_by_device}>
    <Column id=device_type title="Device Type" />
    <Column id=total_txns title="Total Txns" fmt="num0" />
    <Column id=fraud_txns title="Fraud Txns" fmt="num0" />
    <Column id=fraud_rate_pct title="Fraud Rate" fmt="pct2" />
    <Column id=total_fraud_amount title="Fraud Amt" fmt="usd2" />
</DataTable>

### Amount Buckets

<DataTable data={amount_buckets}>
    <Column id=amount_level title="Amount Level" />
    <Column id=total_txns title="Total Txns" fmt="num0" />
    <Column id=fraud_txns title="Fraud Txns" fmt="num0" />
    <Column id=fraud_rate_pct title="Fraud Rate" fmt="pct2" />
    <Column id=total_fraud_amount title="Fraud Amt" fmt="usd2" />
</DataTable>

```sql kpi_overview
SELECT
    SUM(total_transaction) AS total_transactions,
    ROUND(SUM(fraud_transaction) * 1.0 / NULLIF(SUM(total_transaction), 0), 4) AS fraud_rate_pct,
    SUM(fraud_transaction) AS total_fraud_transactions,
    ROUND(SUM(total_fraud_amount) / 1000000.0, 2) AS total_fraud_amount,
    ROUND(SUM(total_amount) / 1000000.0, 2) AS total_amount
FROM bigquery.fraud_risk_summary
```

```sql top_risk_product
SELECT
    product_code AS product,
    ROUND(SUM(fraud_transaction) * 1.0 / NULLIF(SUM(total_transaction), 0), 4) AS fraud_rate_pct
FROM bigquery.fraud_risk_summary
GROUP BY product_code
ORDER BY fraud_rate_pct DESC
LIMIT 1
```

```sql daily
SELECT
    transaction_date,
    SUM(total_transaction) AS total_transactions,
    SUM(fraud_transaction) AS fraud_transactions,
    ROUND(SUM(fraud_transaction) * 1.0 / NULLIF(SUM(total_transaction), 0), 4) AS fraud_rate_pct,
    ROUND(SUM(total_amount), 2) AS total_amount,
    ROUND(SUM(total_fraud_amount), 2) AS total_fraud_amount
FROM bigquery.fraud_risk_summary
GROUP BY transaction_date
ORDER BY transaction_date
```

```sql fraud_by_product
SELECT
    product_code,
    SUM(total_transaction) AS total_transaction,
    SUM(fraud_transaction) AS fraud_transaction,
    ROUND(SUM(fraud_transaction) * 1.0 / NULLIF(SUM(total_transaction), 0), 4) AS fraud_rate_pct,
    SUM(total_fraud_amount) AS total_fraud_amount
FROM bigquery.fraud_risk_summary
GROUP BY product_code
ORDER BY fraud_rate_pct DESC
```

```sql fraud_by_card
SELECT
    COALESCE(NULLIF(card_network, ''), 'other') AS card_network,
    SUM(total_transaction) AS total_txns,
    SUM(fraud_transaction) AS fraud_txns,
    ROUND(SUM(fraud_transaction) * 1.0 / NULLIF(SUM(total_transaction), 0), 4) AS fraud_rate_pct,
    SUM(total_fraud_amount) AS total_fraud_amount
FROM bigquery.fraud_risk_summary
GROUP BY card_network
ORDER BY fraud_rate_pct DESC
```

```sql fraud_by_device
SELECT
    COALESCE(NULLIF(device_type, ''), 'unknown') AS device_type,
    SUM(total_transaction) AS total_txns,
    SUM(fraud_transaction) AS fraud_txns,
    ROUND(SUM(fraud_transaction) * 1.0 / NULLIF(SUM(total_transaction), 0), 4) AS fraud_rate_pct,
    SUM(total_fraud_amount) AS total_fraud_amount
FROM bigquery.fraud_risk_summary
GROUP BY device_type
ORDER BY fraud_rate_pct DESC
```

```sql amount_buckets
SELECT
    amount_level,
    SUM(total_txns) AS total_txns,
    SUM(fraud_txns) AS fraud_txns,
    ROUND(SUM(fraud_txns) * 1.0 / NULLIF(SUM(total_txns), 0), 4) AS fraud_rate_pct,
    ROUND(SUM(total_amt), 2) AS total_amt,
    SUM(total_fraud_amount) AS total_fraud_amount
FROM bigquery.amount_buckets
GROUP BY amount_level
ORDER BY fraud_rate_pct DESC
```