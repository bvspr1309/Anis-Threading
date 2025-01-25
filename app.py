import streamlit as st
from components.customer import add_customer, get_customer_by_phone, get_all_customers, remove_customer_if_combos_used_up
from components.combo import add_combo_type, get_combo_types, delete_combo_type, get_customer_combos
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
        - Manage customers and assign combos.
        - Handle combo packages for discounted services.
        - Schedule and manage appointments with time slots.
        - Track combo usage and appointment history.
    """)

# ============================
# Customer Management
# ============================
elif choice == "Customer Management":
    st.subheader("Customer Management")

    # Add a new customer with a combo
    st.write("### Add a New Customer with Combo")
    name = st.text_input("Customer Name")
    phone = st.text_input("Phone Number")

    # Dropdown to select a combo type
    combo_types = get_combo_types()
    if combo_types:
        combo_type_options = {f"{combo[1]} - {combo[2]} (Uses: {combo[3]})": combo[0] for combo in combo_types}
        selected_combo = st.selectbox("Select a Combo", options=list(combo_type_options.keys()))
        selected_combo_id = combo_type_options[selected_combo]
    else:
        st.warning("No combo types available. Please add combos in the Combo Management tab.")
        selected_combo_id = None

    if st.button("Add Customer with Combo"):
        if selected_combo_id and add_customer(name, phone, selected_combo_id):
            st.success(f"Customer '{name}' added successfully with combo '{selected_combo}'!")
        else:
            st.error("Failed to add the customer. Please ensure the information is correct.")

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

    # Add a new combo type
    st.write("### Add a New Combo Type")
    combo_name = st.text_input("Combo Name")
    services = st.text_area("Services (Comma-separated)", placeholder="e.g., Eyebrow Threading, Facial, Henna Tattoo")
    total_uses = st.number_input("Total Uses", min_value=1, step=1)

    if st.button("Add Combo Type"):
        if add_combo_type(combo_name, services, total_uses):
            st.success(f"Combo type '{combo_name}' added successfully!")
        else:
            st.error("Failed to add the combo type. It may already exist.")

    # View and delete combo types
    st.write("### Existing Combo Types")
    combo_types = get_combo_types()
    if combo_types:
        for combo in combo_types:
            st.write(f"ID: {combo[0]}, Name: {combo[1]}, Services: {combo[2]}, Total Uses: {combo[3]}")
            if st.button(f"Delete Combo '{combo[1]}'", key=f"delete_combo_{combo[0]}"):
                if delete_combo_type(combo[0]):
                    st.success(f"Combo '{combo[1]}' deleted successfully!")
                else:
                    st.error(f"Failed to delete combo '{combo[1]}'.")
    else:
        st.write("No combos found.")

# ============================
# Appointment Management
# ============================
elif choice == "Appointment Management":
    st.subheader("Appointment Management")

    # Book an appointment
    st.write("### Book an Appointment")
    phone = st.text_input("Customer Phone Number (for appointment)")
    service = st.selectbox("Select Service", ["Eyebrow Threading", "Facial", "Henna Tattoo"])
    date = st.date_input("Appointment Date")
    start_time = st.time_input("Start Time")
    end_time = st.time_input("End Time")
    use_combo = st.checkbox("Use Combo")

    if st.button("Book Appointment"):
        customer = get_customer_by_phone(phone)
        if customer:
            customer_id = customer[0]
            if use_combo:
                combos = get_customer_combos(customer_id)
                if combos:
                    combo_id = combos[0][0]  # Use the first available combo
                    if book_appointment(customer_id, service, str(date), str(start_time), str(end_time), combo_id):
                        st.success(f"Appointment booked for {service} on {date} from {start_time} to {end_time} using combo!")
                        remove_customer_if_combos_used_up(customer_id)
                    else:
                        st.error("Failed to book appointment.")
                else:
                    st.error("No active combos available. Book without a combo or add a combo first.")
            else:
                if book_appointment(customer_id, service, str(date), str(start_time), str(end_time)):
                    st.success(f"Appointment booked for {service} on {date} from {start_time} to {end_time}!")
                else:
                    st.error("Failed to book appointment.")
        else:
            st.error("Customer not found. Please add the customer first.")

# ============================
# View Appointments
# ============================
elif choice == "View Appointments":
    st.subheader("View Appointments")

    # View appointments for a customer
    st.write("### Search Appointments by Customer")
    phone_to_check = st.text_input("Enter Customer Phone Number")
    if st.button("View Appointments for Customer"):
        customer = get_customer_by_phone(phone_to_check)
        if customer:
            customer_id = customer[0]
            appointments = get_customer_appointments(customer_id)
            if appointments:
                for appointment in appointments:
                    st.write(f"Appointment ID: {appointment[0]}, Service: {appointment[2]}, Date: {appointment[3]}, Time: {appointment[4]} - {appointment[5]}, Combo ID: {appointment[6]}")
            else:
                st.write("No appointments found for this customer.")
        else:
            st.error("Customer not found.")

    # View appointments for a specific date
    st.write("### Search Appointments by Date")
    date_to_check = st.date_input("Select a Date")
    if st.button("View Appointments by Date"):
        appointments = get_appointment_by_date(str(date_to_check))
        if appointments:
            for appointment in appointments:
                st.write(f"Appointment ID: {appointment[0]}, Customer ID: {appointment[1]}, Service: {appointment[2]}, Time: {appointment[4]} - {appointment[5]}, Combo ID: {appointment[6]}")
        else:
            st.write("No appointments found for this date.")
