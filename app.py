import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


# --------------------------------
# Page Configuration
# --------------------------------

st.set_page_config(
    page_title="Loan & Credit Card Simulator",
    page_icon="💳",
    layout="wide"
)


# --------------------------------
# Custom Styling
# --------------------------------

st.markdown("""
<style>

    .main-title {
        font-size: 36px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        color: #888888;
        font-size: 16px;
        margin-bottom: 30px;
    }

    .section-title {
        font-size: 22px;
        font-weight: 600;
        margin-top: 25px;
        margin-bottom: 15px;
    }

</style>
""", unsafe_allow_html=True)


# --------------------------------
# Header
# --------------------------------

st.markdown(
    '<div class="main-title">Loan & Credit Card Simulator</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Explore how different payment behaviours affect repayment, '
    'interest, and overall cost.'
    '</div>',
    unsafe_allow_html=True
)


# --------------------------------
# Sidebar
# --------------------------------

st.sidebar.title("Loan Details")

amount = st.sidebar.number_input(
    "Loan / Credit Card Amount (RM)",
    min_value=100.0,
    max_value=1000000.0,
    value=10000.0,
    step=500.0
)

interest_rate = st.sidebar.number_input(
    "Annual Interest Rate (%)",
    min_value=0.0,
    max_value=50.0,
    value=12.0,
    step=0.5
)

term = st.sidebar.number_input(
    "Loan Term (Months)",
    min_value=1,
    max_value=360,
    value=24,
    step=1
)

monthly_payment = st.sidebar.number_input(
    "Monthly Payment (RM)",
    min_value=10.0,
    max_value=100000.0,
    value=500.0,
    step=50.0
)

payment_behavior = st.sidebar.selectbox(
    "Payment Behaviour",
    ["On-time", "Early", "Late"]
)


# --------------------------------
# Behaviour Settings
# --------------------------------

if payment_behavior == "Early":

    extra_payment = st.sidebar.slider(
        "Extra Payment (%)",
        10,
        100,
        30
    )

    actual_payment = monthly_payment * (
        1 + extra_payment / 100
    )

    missed_months = 0

elif payment_behavior == "Late":

    missed_months = st.sidebar.slider(
        "Months Missed",
        1,
        6,
        1
    )

    actual_payment = monthly_payment
    extra_payment = 0

else:

    actual_payment = monthly_payment
    extra_payment = 0
    missed_months = 0


# --------------------------------
# Simulation Function
# --------------------------------

def simulate_loan(
    principal,
    annual_rate,
    payment,
    behavior="On-time",
    missed_months=0
):

    monthly_rate = annual_rate / 100 / 12

    balance = principal
    month = 0
    total_interest = 0

    records = []

    while balance > 0 and month < 1000:

        month += 1

        interest = balance * monthly_rate

        total_interest += interest

        if behavior == "Late" and month <= missed_months:
            current_payment = 0

        else:
            current_payment = min(
                payment,
                balance + interest
            )

        principal_paid = current_payment - interest

        if principal_paid < 0:
            principal_paid = 0

        balance -= principal_paid

        if balance < 0:
            balance = 0

        records.append({
            "Month": month,
            "Payment": current_payment,
            "Interest": interest,
            "Principal": principal_paid,
            "Remaining Balance": balance
        })

    return pd.DataFrame(records), total_interest


# --------------------------------
# Current Scenario
# --------------------------------

df, total_interest = simulate_loan(
    amount,
    interest_rate,
    actual_payment,
    payment_behavior,
    missed_months
)

total_repaid = df["Payment"].sum()
payoff_time = len(df)
extra_cost = total_repaid - amount


# --------------------------------
# Summary
# --------------------------------

st.markdown(
    '<div class="section-title">Payment Summary</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Interest",
    f"RM {total_interest:,.2f}"
)

col2.metric(
    "Total Repaid",
    f"RM {total_repaid:,.2f}"
)

col3.metric(
    "Payoff Time",
    f"{payoff_time} months"
)

col4.metric(
    "Extra Cost",
    f"RM {extra_cost:,.2f}"
)


# --------------------------------
# Charts
# --------------------------------

st.markdown(
    '<div class="section-title">Payment Analysis</div>',
    unsafe_allow_html=True
)

chart1, chart2 = st.columns(2)


# --------------------------------
# Chart 1
# --------------------------------

with chart1:

    st.caption("Remaining Balance Over Time")

    fig1, ax1 = plt.subplots()

    ax1.plot(
        df["Month"],
        df["Remaining Balance"],
        linewidth=2
    )

    ax1.set_xlabel("Month")
    ax1.set_ylabel("Balance (RM)")
    ax1.set_title(
        f"{payment_behavior} Payment"
    )

    ax1.grid(
        alpha=0.3
    )

    st.pyplot(
        fig1,
        use_container_width=True
    )


# --------------------------------
# Chart 2
# --------------------------------

on_time_df, on_time_interest = simulate_loan(
    amount,
    interest_rate,
    monthly_payment,
    "On-time",
    0
)

early_df, early_interest = simulate_loan(
    amount,
    interest_rate,
    monthly_payment * 1.3,
    "Early",
    0
)

late_df, late_interest = simulate_loan(
    amount,
    interest_rate,
    monthly_payment,
    "Late",
    2
)

comparison = pd.DataFrame({
    "Behaviour": [
        "On-time",
        "Early",
        "Late"
    ],
    "Interest": [
        on_time_interest,
        early_interest,
        late_interest
    ]
})


with chart2:

    st.caption("Total Interest Comparison")

    fig2, ax2 = plt.subplots()

    ax2.bar(
        comparison["Behaviour"],
        comparison["Interest"]
    )

    ax2.set_ylabel("Interest (RM)")
    ax2.set_title("Interest by Payment Behaviour")

    ax2.grid(
        axis="y",
        alpha=0.3
    )

    st.pyplot(
        fig2,
        use_container_width=True
    )

# --------------------------------
# View 3 - Principal vs Interest
# --------------------------------

st.markdown(
    '<div class="section-title">Payment Breakdown</div>',
    unsafe_allow_html=True
)

pie_col1, pie_col2 = st.columns([1, 1])

with pie_col1:

    principal_paid = df["Principal"].sum()
    interest_paid = df["Interest"].sum()

    fig3, ax3 = plt.subplots()

    ax3.pie(
        [principal_paid, interest_paid],
        labels=["Principal", "Interest"],
        autopct="%1.1f%%",
        startangle=90
    )

    ax3.set_title("Principal vs. Interest")

    st.pyplot(
        fig3,
        use_container_width=True
    )


with pie_col2:

    st.write("### Payment Breakdown")

    st.metric(
        "Principal Paid",
        f"RM {principal_paid:,.2f}"
    )

    st.metric(
        "Interest Paid",
        f"RM {interest_paid:,.2f}"
    )

    st.write(
        "This chart shows how your total payments are divided "
        "between the original amount borrowed and interest."
    )
    
# --------------------------------
# Current Scenario Information
# --------------------------------

st.markdown(
    '<div class="section-title">Current Scenario</div>',
    unsafe_allow_html=True
)

if payment_behavior == "On-time":

    st.info(
        "You are making the standard monthly payment."
    )

elif payment_behavior == "Early":

    st.success(
        f"You are paying {extra_payment}% more "
        "than the standard monthly payment."
    )

else:

    st.warning(
        f"You missed {missed_months} payment(s) "
        "before resuming your normal payment."
    )


# --------------------------------
# Payment Schedule
# --------------------------------

with st.expander("View Detailed Payment Schedule"):

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )