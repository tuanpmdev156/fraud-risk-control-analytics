---
title: Home
theme:
  colors:
    base:
      light: "#FDF8F0"
      dark: "#1A1A1A"
    card:
      light: "#FFFFFF"
      dark: "#24201D"
    cardLayoutBackground:
      light: "#FDF8F0"
      dark: "#1A1A1A"
    positive:
      light: "#2B6B5E"
      dark: "#2B6B5E"
    negative:
      light: "#C23D2E"
      dark: "#C23D2E"
  colorPalettes:
    default:
      light: ["#C23D2E", "#4A7FB5", "#2B6B5E", "#D4890A", "#7B6B8A", "#8C8279"]
      dark: ["#C23D2E", "#4A7FB5", "#2B6B5E", "#D4890A", "#7B6B8A", "#8C8279"]
  fonts:
    heading: serif
    body: sans-serif
    mono: mono
  chart:
    gridlines: true
    gridlineColor:
      light: "#EDE6DA"
    axisLabelColor:
      light: "#8C8279"
    barRadius: 0
---

# Fraud Risk Analytics Dashboard


## Executive Scorecards

{% row %}
  {% big_value
      data="/queries/kpi_overview"
      value="total_transactions"
      title="Transactions Analyzed"
      fmt="num0"
  /%}
  {% big_value
      data="/queries/kpi_overview"
      value="fraud_rate_pct"
      title="Overall Fraud Rate"
      fmt="pct2"
  /%}
  {% big_value
      data="/queries/kpi_overview"
      value="total_fraud_amount"
      title="Fraud Exposure ($M)"
      fmt="usd1"
  /%}
  {% big_value
      data="/queries/top_risk_product"
      value="product"
      title="Highest Risk Product"
  /%}
{% /row %}

---

## Daily Fraud Activity

> Transaction volume and fraud rate across the observation period.

{% combo_chart
    data="/queries/daily"
    x="transaction_date"
    y_fmt="num0"
%}
    {% line y="fraud_transactions" /%}
    {% line y="total_transactions" axis="y1"  /%}
{% /combo_chart %}

---

## Fraud Distribution by Category

> Fraud rate and transaction volume across product codes and card networks.

{% row %}
  {% horizontal_bar_chart
      data="/queries/fraud_by_product"
      y="product_code"
      x="fraud_rate_pct"
      x_axis_options={ 
        title="Fraud Rate %"
        show_title=true 
      }
      bar_options={
          color="#4A7FB5"
      }
      title="BY PRODUCT CODE"
      x_fmt="pct1"
      data_labels={ position = "right" }
  /%}
  {% horizontal_bar_chart
      data="/queries/fraud_by_card"
      y="card_network"
      x="fraud_rate_pct"
      bar_options={
          color="#C23D2E"
      }
      x_axis_options={ 
        title="Fraud Rate %"
        show_title=true 
      }
      title="BY CARD NETWORK"
      x_fmt="pct1"
      data_labels={ position = "right" }
  /%}
{% /row %}

---

## Transaction Profile & Breakdown

> Fraud patterns by client device type and product-level risk breakdown.

{% row %}
  {% horizontal_bar_chart
      data="/queries/fraud_by_device"
      y="device_type"
      x="fraud_rate_pct"
      bar_options={
          color="#2B6B5E"
      }
      x_axis_options={ 
        title="Fraud Rate %"
        show_title=true 
      }
      title="BY DEVICE TYPE"
      x_fmt="pct2"
      data_labels={ position = "right" }
  /%}
  {% table 
    data="/queries/fraud_by_product"
    title="PRODUCT CODE SUMMARY"
    order="fraud_rate_pct desc"
  %}
    {% dimension value="product_code" title="Product" /%}
    {% measure value="total_transaction" title="Total Txns" fmt="num0" /%}
    {% measure value="fraud_transaction" title="Fraud Txns" fmt="num0" /%}
    {% measure value="fraud_rate_pct" title="Fraud Rate" fmt="pct2" /%}
    {% measure value="total_fraud_amount" title="Total Fraud Amt" fmt="usd2" /%}
  {% /table %}
{% /row %}

---

## Risk by Transaction Size

> Fraud rate across amount buckets — higher-value transactions show elevated risk.

{% bar_chart
    data="/queries/amount_buckets"
    x="amount_level"
    y="fraud_rate_pct"
    bar_options={
          color="#D4890A"
      }
    subtitle="Amount buckets: micro(<$50), low($50–$100), medium($100–$500),high($500–$2,000), critical(>$2,000)"
    y_fmt="pct2"
/%}

---

## Data Sources & Inspection

> Queries powering this dashboard, sourced from BigQuery production dataset.

### Daily Trend

{% table data="/queries/daily" order="transaction_date asc"%}
  {% dimension value="transaction_date" title="Transaction Date" /%}
  {% measure value="total_transactions" title="Total Txns" fmt="num0" /%}
  {% measure value="fraud_transactions" title="Fraud Txns" fmt="num0" /%}
  {% measure value="fraud_rate_pct" title="Fraud Rate" fmt="pct2" /%}
  {% measure value="total_amount" title="Total Amount" fmt="usd2" /%}
  {% measure value="total_fraud_amount" title="Fraud Amount" fmt="usd2" /%}
{% /table %}

### By Product Code

{% table data="/queries/fraud_by_product" order="fraud_rate_pct desc" %}
  {% dimension value="product_code" title="Product" /%}
  {% measure value="total_transaction" title="Total Txns" fmt="num0" /%}
  {% measure value="fraud_transaction" title="Fraud Txns" fmt="num0" /%}
  {% measure value="fraud_rate_pct" title="Fraud Rate" fmt="pct2" /%}
  {% measure value="total_fraud_amount" title="Total Fraud Amt" fmt="usd2" /%}
{% /table %}

### By Card Network

{% table data="/queries/fraud_by_card" order="fraud_rate_pct desc" %}
  {% dimension value="card_network" title="Card Network" /%}
  {% measure value="total_txns" title="Total Txns" fmt="num0" /%}
  {% measure value="fraud_txns" title="Fraud Txns" fmt="num0" /%}
  {% measure value="fraud_rate_pct" title="Fraud Rate" fmt="pct2" /%}
  {% measure value="total_fraud_amount" title="Total Fraud Amt" fmt="usd2" /%}
{% /table %}

### By Device Type

{% table data="/queries/fraud_by_device" order="fraud_rate_pct desc" %}
  {% dimension value="device_type" title="Device Type" /%}
  {% measure value="total_txns" title="Total Txns" fmt="num0" /%}
  {% measure value="fraud_txns" title="Fraud Txns" fmt="num0" /%}
  {% measure value="fraud_rate_pct" title="Fraud Rate" fmt="pct2" /%}
  {% measure value="total_fraud_amount" title="Total Fraud Amt" fmt="usd2" /%}
{% /table %}

### Amount Buckets

{% table data="/queries/amount_buckets" order="fraud_rate_pct desc" %}
  {% dimension value="amount_level" title="Amount Level" /%}
  {% measure value="total_txns" title="Total Txns" fmt="num0" /%}
  {% measure value="fraud_txns" title="Fraud Txns" fmt="num0" /%}
  {% measure value="fraud_rate_pct" title="Fraud Rate" fmt="pct2" /%}
  {% measure value="total_fraud_amount" title="Total Fraud Amt" fmt="usd2" /%}
{% /table %}