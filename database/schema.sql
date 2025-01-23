-- ==============================
-- Customers Table
-- ==============================
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique ID for each customer
    name TEXT NOT NULL,                    -- Customer's full name
    phone TEXT NOT NULL UNIQUE             -- Customer's phone number (must be unique)
);

-- ==============================
-- Combos Table
-- ==============================
CREATE TABLE IF NOT EXISTS combos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique ID for each combo purchase
    customer_id INTEGER NOT NULL,          -- Links to the customer who purchased the combo
    combo_name TEXT NOT NULL,              -- Name of the combo (e.g., "Eyebrow Threading Combo")
    total_uses INTEGER NOT NULL,           -- Total number of times the combo can be used
    remaining_uses INTEGER NOT NULL,       -- Remaining uses available for this combo
    FOREIGN KEY (customer_id) REFERENCES customers (id)  -- Link to the customers table
);

-- ==============================
-- Appointments Table
-- ==============================
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique ID for each appointment
    customer_id INTEGER NOT NULL,          -- Links to the customer booking the appointment
    service TEXT NOT NULL,                 -- Service booked (e.g., "Eyebrow Threading")
    date TEXT NOT NULL,                    -- Appointment date (stored as text in YYYY-MM-DD format)
    combo_id INTEGER,                      -- Links to the combo used (if any)
    FOREIGN KEY (customer_id) REFERENCES customers (id), -- Link to the customers table
    FOREIGN KEY (combo_id) REFERENCES combos (id)        -- Link to the combos table
);

-- ==============================
-- Indexes for Optimization
-- ==============================
-- Index to quickly find customers by phone number
CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers (phone);

-- Index to quickly find active combos for a specific customer
CREATE INDEX IF NOT EXISTS idx_combos_customer_id ON combos (customer_id);

-- Index to quickly retrieve appointments by customer ID
CREATE INDEX IF NOT EXISTS idx_appointments_customer_id ON appointments (customer_id);
