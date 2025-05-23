import streamlit as st
import pandas as pd
from datetime import date, datetime

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
        columns=['Timestamp', 'Date', 'Category', 'Subsegment', 'Amount', 'Notes']
    )

# ─── 2. Timezone setup ───────────────────────────────────────────────────────
try:
    from zoneinfo import ZoneInfo
    pacific = ZoneInfo("America/Los_Angeles")
except ImportError:
    import pytz
    pacific = pytz.timezone("America/Los_Angeles")

# ─── 3. Default widget values in session state ───────────────────────────────
placeholder = "-- Select Category --"
if 'entry_date' not in st.session_state:
    st.session_state.entry_date = datetime.now(pacific).date()
if 'category' not in st.session_state:
    st.session_state.category = placeholder

st.title("Budget Entry Form")

# ─── 4. Date and Category Selection ─────────────────────────────────────────
entry_date = st.date_input(
    "Select Date",
    key='entry_date'
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

# ─── 5. Conditional Subfields & Submission ───────────────────────────────────
if category != placeholder:
    subsegments_map = {
        "Food and Drink": [
            "Small meal / Coffee / Drink (<$20)",
            "Eating Out / Happy Hour ($20 -> $120)",
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
            key='subcat', format_func=lambda x: x.replace("$", r"\$")
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
        key='amount_input'
    ).strip()
    notes = st.text_area(
        "Additional Notes",
        key='notes'
    ).strip()

    def submit_and_reset():
        try:
            amt = float(st.session_state.amount_input)
        except ValueError:
            st.error("⚠️ Invalid amount. Please enter a number.")
            return
        now = datetime.now(pacific)
        ts = f"{now.month}/{now.day}/{now.year} {now.hour:02}:{now.minute:02}:{now.second:02}"
        d = st.session_state.entry_date
        date_str = f"{d.month}/{d.day}/{d.year}"
        new_entry = {
            'Timestamp': ts,
            'Date': date_str,
            'Category': st.session_state.category,
            'Subsegment': subcat,
            'Amount': amt,
            'Notes': st.session_state.notes
        }
        st.session_state.budget = pd.concat(
            [st.session_state.budget, pd.DataFrame([new_entry])],
            ignore_index=True
        )
        st.session_state.entry_date = datetime.now(pacific).date()
        st.session_state.category = placeholder
        st.session_state.subcat = None
        st.session_state.other_subcat = ""
        st.session_state.amount_input = ""
        st.session_state.notes = ""
        st.success("Entry added to budget dataset!")

    st.button("Submit Entry", on_click=submit_and_reset)
else:
    st.info("⚠️ Please select a category to see and submit an entry.")

# ─── 6. Display current entries ───────────────────────────────────────────────
st.subheader("New Budget Entries")
st.dataframe(st.session_state.budget)
