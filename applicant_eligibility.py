import streamlit as st

def check_eligibility(customer):
    cibil_threshold = 550

    # Check customer eligibility
    if customer['cibil'] < cibil_threshold:
        return {'status': 'Not Eligible', 'reason': 'Customer CIBIL score is below the threshold.'}
    if customer['income'] <= 16000:
        return {'status': 'Not Eligible', 'reason': 'Customer income is below the threshold.'}

    # If customer is eligible
    return {
        'status': 'Eligible',
        'remaining_income': customer['income'] * 0.7 - sum(customer['emi_list'])
    }

# If customer is not eligible, check co-applicant eligibility
def check_co_applicant_eligibility(customer, co_applicant):
    cibil_threshold = 550

    total_income = customer['income'] + customer['additional_income'] + co_applicant['income'] + co_applicant['additional_income']

    if co_applicant['cibil'] < cibil_threshold and customer['cibil'] < cibil_threshold:
        return {'status': 'Not Eligible', 'reason': 'Both Applicant and Co-Applicant CIBIL scores are below the threshold.'}
    if total_income <= 16000:
        return {'status': 'Not Eligible', 'reason': 'Total income is below the threshold.'}

    return {
        'status': 'Eligible with Co-Applicant',
        'remaining_income': (total_income * 0.7) - (sum(customer['emi_list']) + sum(co_applicant['emi_list']))
    }

# Streamlit application
st.title("Something Something Something")

# Collect customer details
st.header("Applicant Details")
customer_income = st.number_input("Enter your monthly income:", min_value=0)
customer_additional_income = st.number_input("Enter your additional monthly income (default is 0):", min_value=0, value=0)
customer_cibil = st.number_input("Enter your CIBIL score:", min_value=0)
customer_emis = st.text_input("Enter your existing EMIs (comma-separated):")

# Process the existing EMIs
customer_emi_list = list(map(int, customer_emis.split(','))) if customer_emis else []

# Create customer data dictionary
customer_data = {
    'income': customer_income,
    'additional_income': customer_additional_income,
    'cibil': customer_cibil,
    'emi_list': customer_emi_list
}

# Ask if co-applicant is available
result_with_co_applicant = None
if st.checkbox("Do you have a co-applicant?"):
    st.header("Co-Applicant Details")
    co_applicant_income = st.number_input("Enter co-applicant's monthly income:", min_value=0)
    co_applicant_additional_income = st.number_input("Enter co-applicant's additional monthly income (default is 0):", min_value=0, value=0)
    co_applicant_cibil = st.number_input("Enter co-applicant's CIBIL score:", min_value=0)
    co_applicant_emis = st.text_input("Enter co-applicant's existing EMIs (comma-separated):")

    # Process co-applicant existing EMIs
    co_applicant_emi_list = list(map(int, co_applicant_emis.split(','))) if co_applicant_emis else []

    # Create co-applicant data dictionary
    co_applicant_data = {
        'income': co_applicant_income,
        'additional_income': co_applicant_additional_income,
        'cibil': co_applicant_cibil,
        'emi_list': co_applicant_emi_list
    }

    # Check eligibility with co-applicant
    result_with_co_applicant = check_co_applicant_eligibility(customer_data, co_applicant_data)

# Check eligibility
result = check_eligibility(customer_data)

if result['status'] == 'Eligible':
    # Update remaining income if co-applicant exists and is eligible
    if result_with_co_applicant and result_with_co_applicant['status'] == 'Eligible with Co-Applicant':
        result['remaining_income'] = result_with_co_applicant['remaining_income']
        result['status'] = 'Eligible with Co-Applicant'
    st.success(f"You are eligible for the loan! Remaining Income: {result['remaining_income']:.2f}")
else:
    st.warning(f"You are not eligible for the loan. Reason: {result['reason']}")

    # If co-applicant is available and eligible
    if result_with_co_applicant and result_with_co_applicant['status'] == 'Eligible with Co-Applicant':
        st.success(f"You are eligible for the loan with your co-applicant! Remaining Income: {result_with_co_applicant['remaining_income']:.2f}")

# Loan Details Section
st.header("Loan Details")
loan_amount = st.number_input("Enter the loan amount:", min_value=0)
tenure = st.number_input("Enter the loan tenure (in months):", min_value=0)
rate_of_interest = st.number_input("Enter the rate of interest (default is 12%):", min_value=0.0, value=12.0)

# Calculate EMI using the formula
if loan_amount > 0 and tenure > 0 and rate_of_interest > 0:
    monthly_interest_rate = rate_of_interest / (12 * 100)
    emi = (loan_amount * monthly_interest_rate * (1 + monthly_interest_rate) ** tenure) / ((1 + monthly_interest_rate) ** tenure - 1)
    st.write(f"Your monthly EMI is: {emi:.2f}")

    # Check if remaining income is greater than EMI
    if result['remaining_income'] >= emi:
        st.success("You are eligible for the loan based on your remaining income.")
    else:
        st.warning("You are not eligible for the loan as your remaining income is less than the EMI.")
