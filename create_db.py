import sqlite3

conn = sqlite3.connect("clients.db")
cursor = conn.cursor()

#usuarios del sistema (no clientes)
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE,
    role TEXT CHECK(role IN ('admin', 'staff', 'viewer')) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

#clientes
cursor.execute("""
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    status TEXT CHECK(status IN ('lead', 'active', 'inactive', 'archived')) DEFAULT 'lead',
    industry TEXT,
    website TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
)
""")

#direcciones de clientes (relacion 1 a n)
cursor.execute("""
CREATE TABLE IF NOT EXISTS addresses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    type TEXT CHECK(type IN ('billing', 'shipping', 'office')) NOT NULL,
    street TEXT,
    city TEXT,
    state TEXT,
    postal_code TEXT,
    country TEXT,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
)
""")

#contactos de clientes (relacion 1 a n)
cursor.execute("""
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    position TEXT,
    is_primary INTEGER DEFAULT 0,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
)
""")

#información sensible de clientes (relacion 1 a 1)
cursor.execute("""
CREATE TABLE IF NOT EXISTS client_pii (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL UNIQUE,
    national_id TEXT,
    tax_id TEXT,
    bank_iban TEXT,
    credit_card_number TEXT,
    credit_card_last4 TEXT,
    date_of_birth DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
)
""")

#proyectos de clientes (relacion 1 a n)
cursor.execute("""
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT CHECK(status IN ('planned', 'active', 'completed', 'cancelled')) DEFAULT 'planned',
    start_date DATE,
    end_date DATE,
    budget REAL,
    FOREIGN KEY (client_id) REFERENCES clients(id)
)
""")

#facturas de clientes (relacion 1 a n)
cursor.execute("""
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    project_id INTEGER,
    invoice_number TEXT UNIQUE NOT NULL,
    amount REAL NOT NULL,
    status TEXT CHECK(status IN ('draft', 'sent', 'paid', 'overdue')) DEFAULT 'draft',
    issue_date DATE,
    due_date DATE,
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (project_id) REFERENCES projects(id)
)
""")

#pagos de clientes (relacion 1 a n)
cursor.execute("""
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    payment_method TEXT,
    payment_date DATE DEFAULT CURRENT_DATE,
    reference TEXT,
    FOREIGN KEY (invoice_id) REFERENCES invoices(id)
)
""")

#interacciones (historial CRM)
cursor.execute("""
CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    user_id INTEGER,
    type TEXT CHECK(type IN ('call', 'email', 'meeting', 'note')) NOT NULL,
    summary TEXT NOT NULL,
    interaction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

# registros de auditoria (registro a nivel de sistema)
cursor.execute("""
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    entity TEXT NOT NULL,
    entity_id INTEGER,
    action TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")



# =========================
# INDEXES (performance)
# =========================
cursor.execute("CREATE INDEX IF NOT EXISTS idx_clients_status ON clients(status)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_contacts_client ON contacts(client_id)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_sensitive_client ON client_pii(client_id)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_projects_client ON projects(client_id)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_client ON invoices(client_id)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_interactions_client ON interactions(client_id)")

conn.commit()
conn.close()

print("CRM database created successfully.")
