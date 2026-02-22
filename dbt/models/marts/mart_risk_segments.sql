with credit as (
    select * from {{ ref('mart_credit_features') }}
)

select
    customer_id,
    loan_id,
    is_defaulted,
    loan_amount,
    repayment_ratio,
    case
        when betting_spend_ratio > 0.1 then 'high_risk'
        when inflow_outflow_ratio < 0.5 then 'high_risk'
        when balance_volatility > 10000 and avg_balance < 500 then 'high_risk'
        when utility_payment_ratio > 0.1 and inflow_outflow_ratio > 1.0 then 'low_risk'
        when transaction_frequency > 0.5 and avg_balance > 1000 then 'low_risk'
        else 'medium_risk'
    end as risk_segment,
    betting_spend_ratio,
    inflow_outflow_ratio,
    avg_balance,
    transaction_frequency,
    utility_payment_ratio
from credit
