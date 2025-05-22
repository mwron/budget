import streamlit as st
import pandas as pd
from datetime import date

# ─── 0. Password protection ────────────────────────────────────────────────────
pwd = st.text_input("Enter password", type="password")
if "PASSWORD" not in st.secrets:
    st.error("App not configured. Please set PASSWORD in your Streamlit secrets.")
    st.stop()
if pwd != st.secrets["PASSWORD"]:
    st.warning("🔒 Unauthorized. Please enter the correct password.")
    st.stop()

# ─── 1. Initialize budget DataFrame in session state ─────────────────────────
if 'budget' not in st.session_state:
    st.session_state.budget = pd.DataFrame(
        columns=['Date', 'Category', 'Subsegment', 'Amount', 'Notes']
    )

# ─── 2. Ensure default values for entry_date and category ────────────────────
placeholder = "-- Select Category --"
if 'entry_date' not in st.session_state:
    st.session_state.entry_date = date.today()
if 'category' not in st.session_state:
    st.session_state.category = placeholder

st.title("Budget Entry Form")

# ─── 3. Date and category widgets bound to session state ────────────────────
entry_date = st.date_input(
    "Select Date",
    key="entry_date"
)

categories = [placeholder,
    "Food and Drink", "Groceries & Home Essentials",
    "Shopping / Self Care / Gym", "Entertainment / Memberships",
    "Gifts / Donations / Balikbayan", "Home and Taxes",
    "Short Travel (Gas, Car Wash, Transit within SD)",
    "Travel (non-driving, lodging, outside SD)",
    "Car Yearly (Maintenance, Registration)", "Health Misc"
]
category = st.radio(
    "Select Budget Category", options=categories,
    index=categories.index(st.session_state.category),
    key='category'
)

# ─── 4. Show subfields & submit button only when a real category is selected ─
if category != placeholder:
    # Subsegment mapping
    subsegments_map = {
        "Food and Drink": [
            "Eating Out / Happy Hour ($20 -> $120)",
            "Small meal / Coffee / Drink (<$20)",
            "Big Dinner / Treating Others (<$120)"
        ],
        "Groceries & Home Essentials": [],
        "Shopping / Self Care / Gym": ["Gym", "Amazon", "Clothes", "Nails & Hair", "Dry Cleaners"],
        "Entertainment / Memberships": ["Spotify", "SiriusXM", "Apple Storage", "Event Tickets"],
        "Gifts / Donations / Balikbayan": [],
        "Home and Taxes": ["Rent / Home Help", "Income Tax", "Insurance"],
        "Short Travel (Gas, Car Wash, Transit within SD)": ["Gas", "Lyft / Uber", "Public Transit", "Car Wash", "Parking"],
        "Travel (non-driving, lodging, outside SD)": [
            "Flight", "Hotel / AirBnb / Lodging", "Long Train", "Event", "Food", "Travel Gear Misc"
        ],
        "Car Yearly (Maintenance, Registration)": ["Oil Change", "Car Insurance", "Registration", "Tires", "Smog Check"],
        "Health Misc": ["Prescriptions", "Emergency Room", "CoPay", "Glasses / Contacts"]
    }
    opts = subsegments_map.get(category, []).copy()
    if opts:
        opts.append("Other")
        subcat = st.radio(
            "Select Subsegment", options=opts,
            key='subcat'
        )
        if subcat == "Other":
            subcat = st.text_input(
                "Please specify subsegment", key='other_subcat'
            ).strip()
    else:
        subcat = ""

    amount_input = st.text_input(
        "Transaction Total",
        placeholder="e.g. 42.50",
        value=st.session_state.get('amount_input', ""),
        key='amount_input'
    ).strip()
    notes = st.text_area(
        "Additional Notes",
        value=st.session_state.get('notes', ""),
        key='notes'
    ).strip()

    # Callback: append row and reset date & category
    def submit_and_reset():
        try:
            amt = float(st.session_state.amount_input)
        except ValueError:
            st.error("⚠️ Invalid amount. Please enter a number.")
            return
        new_entry = {
            'Date': st.session_state.entry_date,
            'Category': st.session_state.category,
            'Subsegment': subcat,
            'Amount': amt,
            'Notes': st.session_state.notes
        }
        st.session_state.budget = pd.concat(
            [st.session_state.budget, pd.DataFrame([new_entry])],
            ignore_index=True
        )
        # Reset only date and category
        st.session_state.entry_date = date.today()
        st.session_state.category = placeholder
        # Clear the other inputs (optional)
        st.session_state.subcat = None
        st.session_state.other_subcat = ""
        st.session_state.amount_input = ""
        st.session_state.notes = ""
        st.success("Entry added to budget dataset!")

    st.button("Submit Entry", on_click=submit_and_reset)
else:
    st.info("⚠️ Please select a category to see and submit an entry.")

# ─── 5. Display current entries ───────────────────────────────────────────────
st.subheader("New Budget Entries")
st.dataframe(st.session_state.budget)
