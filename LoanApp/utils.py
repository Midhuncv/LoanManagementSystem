from decimal import Decimal
from datetime import datetime, timedelta

def calculate_loan(amount, tenure, interest_rate):
    amount = Decimal(str(amount))
    tenure = int(tenure)
    interest_rate = Decimal(str(interest_rate)) / Decimal('100')  # yearly rate

    # Monthly interest rate
    monthly_rate = interest_rate / Decimal('12')
    
    # EMI formula: P * r * (1 + r)^n / [(1 + r)^n - 1]
    monthly_installment = (amount * monthly_rate * (1 + monthly_rate) ** tenure) / \
                         ((1 + monthly_rate) ** tenure - 1)
    monthly_installment = monthly_installment.quantize(Decimal('0.01'))

    total_amount = monthly_installment * tenure
    total_interest = total_amount - amount

    # Payment schedule
    schedule = []
    balance = amount
    today = datetime.today()
    for i in range(1, tenure + 1):
        interest = balance * monthly_rate
        principal = monthly_installment - interest
        balance -= principal
        due_date = today + timedelta(days=30 * i)
        schedule.append({
            'installment_no': i,
            'due_date': due_date.date(),
            'amount': monthly_installment
        })

    return {
        'monthly_installment': monthly_installment,
        'total_amount': total_amount.quantize(Decimal('0.01')),
        'total_interest': total_interest.quantize(Decimal('0.01')),
        'payment_schedule': schedule
    }