with loans as (
    select * from {{ ref('stg_loan_repayments') }}
)

select
    customer_id,
    loan_id,
    loan_type,
    funded_date,
    due_date,
    loan_duration,
    loan_amount,
    amount_to_repay,
    interest_amount,
    repaid_amount,
    loan_balance,
    last_paid_date,
    is_defaulted,
    repaid_amount * 1.0 / nullif(amount_to_repay, 0) as repayment_ratio,
    case
        when last_paid_date is not null
        then datediff('day', due_date, last_paid_date)
        else null
    end as days_past_due
from loans
