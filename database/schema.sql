-- ============================
-- Customers Table
-- ============================
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique ID for each customer
    name TEXT NOT NULL,                    -- Customer's full name
    phone TEXT NOT NULL UNIQUE             -- Customer's phone number (must be unique)
);

-- ============================
-- Combos Table
-- ============================
CREATE TABLE IF NOT EXISTS combos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique ID for each combo purchase
    customer_id INTEGER NOT NULL,          -- Links to the customer who purchased the combo
    combo_type_id INTEGER NOT NULL,        -- Links to the combo type definition
    remaining_uses INTEGER NOT NULL,       -- Remaining uses available for this combo
    FOREIGN KEY (customer_id) REFERENCES customers (id),  -- Link to the customers table
    FOREIGN KEY (combo_type_id) REFERENCES combo_types (id) -- Link to the combo_types table
);

-- ============================
-- Combo Types Table
-- ============================
CREATE TABLE IF NOT EXISTS combo_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique ID for each combo type
    name TEXT NOT NULL UNIQUE,             -- Combo name (e.g., "Eyebrow Threading Combo")
    services TEXT NOT NULL,                -- JSON or comma-separated list of services
    total_uses INTEGER NOT NULL            -- Total number of uses allowed for this combo
);

-- ============================
-- Preload Combos
-- ============================
INSERT INTO combo_types (name, services, total_uses) VALUES
('Eyebrow Threading Combo', 'Eyebrow Threading', 5),
('Lip, Chin, Forehead Threading Combo', 'Lip, Chin Threading, Forehead', 5),
('Sideburns, Cheeks Threading Combo', 'Sideburns, Cheeks', 5),
('Full Face Threading Combo', 'Full face Threading', 5),
('Ear, Nose Waxing Combo', 'Ear, Nose Waxing', 5),
('Full Leg Waxing Combo', 'Full Leg Waxing', 5),
('Half Leg Waxing Combo', 'Half Leg Waxing', 5),
('Full Arm Waxing Combo', 'Full Arm Waxing', 5),
('Half Arm Waxing Combo', 'Half Arm Waxing', 5),
('Under Arm Waxing Combo', 'Under Arm Waxing', 5),
('Bikini Waxing Combo', 'Bikini Waxing', 5),
('Brazilian Waxing Combo', 'Brazilian Waxing', 5),
('Stomach Waxing Combo', 'Stomach Waxing', 5),
('Back Waxing Combo', 'Back Waxing', 5),
('Full Body Waxing Combo', 'Full Body Waxing', 5),
('Express Facial Combo', 'Express Facial', 5),
('Acne Facial', 'Acne Facial', 5),
('Shehnaz Gold Facial', 'Shehnaz Gold Facial', 5),
('Anis Signature Facial', 'Anis Signature Facial', 5),
('Ayurveda Haldi Chandan Facial', 'Ayurveda Haldi Chandan Facial', 5),
('Microdermabrasion Facial', 'Microdermabrasion Facial', 5),
('Hydra Facial', 'Hydra Facial', 5),
('Radio Frequency Treatment', 'Radio Frequency Treatment', 5),
('Teen Clean Facial', 'Teen Clean Facial', 5),
('Herbal Pearl Glow Facial', 'Herbal Pearl Glow Facial', 5),
('Classic Soothing Regular Facial', 'Classic Soothing Regular Facial', 5);

-- ============================
-- Appointments Table
-- ============================
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique ID for each appointment
    customer_id INTEGER NOT NULL,          -- Links to the customer booking the appointment
    service TEXT NOT NULL,                 -- Service booked (e.g., "Eyebrow Threading")
    date TEXT NOT NULL,                    -- Appointment date (YYYY-MM-DD)
    start_time TEXT,                       -- Start time of the appointment (HH:MM format)
    end_time TEXT,                         -- End time of the appointment (HH:MM format)
    combo_id INTEGER,                      -- Links to the combo being used (if any)
    FOREIGN KEY (customer_id) REFERENCES customers (id), -- Link to the customers table
    FOREIGN KEY (combo_id) REFERENCES combos (id)        -- Link to the combos table
);

-- ============================
-- Indexes for Optimization
-- ============================
-- Index to quickly find customers by phone number
CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers (phone);

-- Index to quickly find combos for a specific customer
CREATE INDEX IF NOT EXISTS idx_combos_customer_id ON combos (customer_id);

-- Index to quickly retrieve appointments by customer ID
CREATE INDEX IF NOT EXISTS idx_appointments_customer_id ON appointments (customer_id);

-- Index to quickly find appointments by date
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments (date);
