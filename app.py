import streamlit as st
from components.customer import add_customer, get_customer_by_phone, get_all_customers
from components.combo import add_combo, get_customer_combos, update_combo_usage, get_combo_status
from components.appointment import book_appointment, get_customer_appointments, get_appointment_by_date

# Set the title of the app
st.title("Ani's Threading and Skincare Management System")

# Sidebar menu
menu = ["Home", "Customer Management", "Combo Management", "Appointment Management", "View Appointments"]
choice = st.sidebar.selectbox("Menu", menu)

# ============================
# Home Page
# ============================
if choice == "Home":
    st.subheader("Welcome to Ani's Threading and Skincare Management System!")
    st.write("""
        This system allows you to:
        - Manage customers.
        - Handle combo packages for discounted services.
        - Schedule and manage appointments.
        - Track combo usage and appointment history.
    """)

# ============================
# Customer Management
# ============================
elif choice == "Customer Management":
    st.subheader("Customer Management")
    # Add a new customer
    st.write("### Add a New Customer")
    name = st.text_input("Customer Name")
    phone = st.text_input("Phone Number")
    if st.button("Add Customer"):
        if add_customer(name, phone):
            st.success(f"Customer '{name}' added successfully!")
        else:
            st.error("A customer with this phone number already exists.")
    
    # View all customers
    st.write("### All Customers")
    customers = get_all_customers()
    if customers:
        for customer in customers:
            st.write(f"ID: {customer[0]}, Name: {customer[1]}, Phone: {customer[2]}")
    else:
        st.write("No customers found.")

# ============================
# Combo Management
# ============================
elif choice == "Combo Management":
    st.subheader("Combo Management")
    st.write("### Add a New Combo for a Customer")
    phone = st.text_input("Customer Phone Number (for combo)")
    combo_name = st.selectbox("Select Combo", ["Eyebrow Threading Combo"])
    total_uses = 5

    if st.button("Add Combo"):
        customer = get_customer_by_phone(phone)
        if customer:
            customer_id = customer[0]
            if add_combo(customer_id, combo_name, total_uses):
                st.success(f"Combo '{combo_name}' added successfully for {customer[1]}!")
            else:
                st.error("Failed to add the combo.")
        else:
            st.error("Customer not found. Please add the customer first.")

    # View all combos for a customer
    st.write("### View Combos for a Customer")
    phone_to_check_combos = st.text_input("Enter Customer Phone Number to View Combos")
    if st.button("View Combos"):
        customer = get_customer_by_phone(phone_to_check_combos)
        if customer:
            customer_id = customer[0]
            combos = get_customer_combos(customer_id)
            if combos:
                for combo in combos:
                    st.write(f"Combo ID: {combo[0]}, Name: {combo[2]}, Remaining Uses: {combo[4]}/{combo[3]}")
            else:
                st.write("No active combos found for this customer.")
        else:
            st.error("Customer not found.")

# ============================
# Appointment Management
# ============================
elif choice == "Appointment Management":
    st.subheader("Appointment Management")
    st.write("### Book an Appointment")
    phone = st.text_input("Customer Phone Number (for appointment)")
    service = st.selectbox("Select Service", ["Eyebrow Threading", "Facial", "Henna Tattoo"])
    date = st.date_input("Appointment Date")
    use_combo = st.checkbox("Use Combo")

    if st.button("Book Appointment"):
        customer = get_customer_by_phone(phone)
        if customer:
            customer_id = customer[0]
            if use_combo:
                combos = get_customer_combos(customer_id)
                if combos:
                    combo_id = combos[0][0]  # Use the first available combo
                    if book_appointment(customer_id, service, str(date), combo_id):
                        update_combo_usage(combo_id)
                        st.success(f"Appointment booked for {service} on {date} using combo!")
                    else:
                        st.error("Failed to book appointment.")
                else:
                    st.error("No active combos available. Book without a combo or add a combo first.")
            else:
                if book_appointment(customer_id, service, str(date)):
                    st.success(f"Appointment booked for {service} on {date}!")
                else:
                    st.error("Failed to book appointment.")
        else:
            st.error("Customer not found. Please add the customer first.")

# ============================
# View Appointments
# ============================
elif choice == "View Appointments":
    st.subheader("View Appointments")
    st.write("### Search Appointments by Customer or Date")
    
    # View appointments for a customer
    phone_to_check_appointments = st.text_input("Enter Customer Phone Number to View Appointments")
    if st.button("View Appointments for Customer"):
        customer = get_customer_by_phone(phone_to_check_appointments)
        if customer:
            customer_id = customer[0]
            appointments = get_customer_appointments(customer_id)
            if appointments:
                for appointment in appointments:
                    st.write(f"Appointment ID: {appointment[0]}, Service: {appointment[2]}, Date: {appointment[3]}, Combo ID: {appointment[4]}")
            else:
                st.write("No appointments found for this customer.")
        else:
            st.error("Customer not found.")
    
    # View appointments for a specific date
    date_to_check_appointments = st.date_input("Select a Date to View Appointments")
    if st.button("View Appointments by Date"):
        appointments = get_appointment_by_date(str(date_to_check_appointments))
        if appointments:
            for appointment in appointments:
                st.write(f"Appointment ID: {appointment[0]}, Customer ID: {appointment[1]}, Service: {appointment[2]}, Combo ID: {appointment[4]}")
        else:
            st.write("No appointments found for this date.")
