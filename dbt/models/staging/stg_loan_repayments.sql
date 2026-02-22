with source as (
    select * from raw_loan_repayments
)

select
    customer_id,
    loan_id,
    new_repeat as loan_type,
    cast(Funded_date as date) as funded_date,
    cast(due_date as date) as due_date,
    loan_duration,
    loan_amount,
    to_repay as amount_to_repay,
    interest_amount,
    repaid_amount,
    loan_balance,
    cast(last_paid_date as date) as last_paid_date,
    case
        when loan_balance <= 0 then 0
        else 1
    end as is_defaulted
from source
