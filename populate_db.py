import sqlite3
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

COUNTRY_PROFILES = [
    {"country": "United States", "locale": "en_US", "state_provider": "state"},
    {"country": "Canada", "locale": "en_CA", "state_provider": "province"},
    {"country": "United Kingdom", "locale": "en_GB", "state_provider": "county"},
    {"country": "Spain", "locale": "es_ES", "state_provider": "autonomous_community"},
    {"country": "France", "locale": "fr_FR", "state_provider": "region"},
    {"country": "Germany", "locale": "de_DE", "state_provider": "state"},
    {"country": "Mexico", "locale": "es_MX", "state_provider": "state"},
    {"country": "Brazil", "locale": "pt_BR", "state_provider": "state"},
    {"country": "Argentina", "locale": "es_AR", "state_provider": "province"},
    {"country": "Chile", "locale": "es_CL", "state_provider": "region"},
    {"country": "Colombia", "locale": "es_CO", "state_provider": "state"},
    {"country": "Peru", "locale": "es_PE", "state_provider": "state"},
    {"country": "Italy", "locale": "it_IT", "state_provider": "region"},
    {"country": "Netherlands", "locale": "nl_NL", "state_provider": "province"},
    {"country": "Australia", "locale": "en_AU", "state_provider": "state"},
    {"country": "Japan", "locale": "ja_JP", "state_provider": "prefecture"},
]

COUNTRY_WEIGHTS = [
    18, 6, 8, 6, 6, 6, 6, 5, 4, 4, 5, 4, 5, 4, 6, 3
]

conn = sqlite3.connect("clients.db")
cursor = conn.cursor()


def random_date(start_days_ago=365):
    return fake.date_between(start_date=f"-{start_days_ago}d", end_date="today")


def _safe_provider(fake_instance, provider_name, fallback):
    provider = getattr(fake_instance, provider_name, None)
    if callable(provider):
        try:
            value = provider()
            if value:
                return value
        except Exception:
            pass
    return fallback() if callable(fallback) else fallback


def generate_address():
    profile = random.choices(COUNTRY_PROFILES, weights=COUNTRY_WEIGHTS, k=1)[0]
    try:
        locale_fake = Faker(profile["locale"])
    except AttributeError:
        locale_fake = Faker("en_US")
    street = locale_fake.street_address()
    city = locale_fake.city()
    state = _safe_provider(locale_fake, profile.get("state_provider", "state"), locale_fake.city)
    postal_code = _safe_provider(locale_fake, "postcode", locale_fake.postcode)
    return {
        "country": profile["country"],
        "street": street,
        "city": city,
        "state": state,
        "postal_code": postal_code,
    }


def generate_sensitive_info():
    national_id = _safe_provider(fake, "ssn", fake.uuid4)
    tax_id = _safe_provider(fake, "ein", fake.uuid4)
    bank_iban = _safe_provider(fake, "iban", fake.bban)
    credit_card_number = fake.credit_card_number()
    credit_card_last4 = credit_card_number[-4:]
    date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=80)
    return {
        "national_id": str(national_id),
        "tax_id": str(tax_id),
        "bank_iban": str(bank_iban),
        "credit_card_number": str(credit_card_number),
        "credit_card_last4": str(credit_card_last4),
        "date_of_birth": date_of_birth
    }

#users
user_ids = []
for _ in range(5):
    cursor.execute("""
        INSERT INTO users (username, full_name, email, role)
        VALUES (?, ?, ?, ?)
    """, (
        fake.user_name(),
        fake.name(),
        fake.email(),
        random.choice(["admin", "staff", "viewer"])
    ))
    user_ids.append(cursor.lastrowid)

#clients
client_ids = []
for _ in range(20):
    cursor.execute("""
        INSERT INTO clients (company_name, status, industry, website, notes, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        fake.company(),
        random.choice(["lead", "active", "inactive"]),
        fake.bs(),
        fake.url(),
        fake.text(max_nb_chars=200),
        datetime.now()
    ))
    client_ids.append(cursor.lastrowid)

#addresses
for client_id in client_ids:
    for addr_type in ["billing", "office"]:
        address = generate_address()
        cursor.execute("""
            INSERT INTO addresses (client_id, type, street, city, state, postal_code, country)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            client_id,
            addr_type,
            address["street"],
            address["city"],
            address["state"],
            address["postal_code"],
            address["country"]
        ))

#client_pii
for client_id in client_ids:
    sensitive = generate_sensitive_info()
    cursor.execute("""
        INSERT INTO client_pii (
            client_id, national_id, tax_id, bank_iban, credit_card_number,
            credit_card_last4, date_of_birth, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        client_id,
        sensitive["national_id"],
        sensitive["tax_id"],
        sensitive["bank_iban"],
        sensitive["credit_card_number"],
        sensitive["credit_card_last4"],
        sensitive["date_of_birth"],
        datetime.now()
    ))

#contacts
contact_ids = []
for client_id in client_ids:
    for i in range(random.randint(1, 3)):
        cursor.execute("""
            INSERT INTO contacts (client_id, first_name, last_name, email, phone, position, is_primary)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            client_id,
            fake.first_name(),
            fake.last_name(),
            fake.email(),
            fake.phone_number(),
            fake.job(),
            1 if i == 0 else 0
        ))
        contact_ids.append(cursor.lastrowid)

#projects
project_ids = []
for client_id in client_ids:
    for _ in range(random.randint(1, 3)):
        cursor.execute("""
            INSERT INTO projects (client_id, name, description, status, start_date, end_date, budget)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            client_id,
            fake.catch_phrase(),
            fake.text(150),
            random.choice(["planned", "active", "completed"]),
            random_date(300),
            random_date(30),
            round(random.uniform(5000, 50000), 2)
        ))
        project_ids.append(cursor.lastrowid)

#invoices
invoice_ids = []
for project_id in project_ids:
    amount = round(random.uniform(1000, 15000), 2)
    cursor.execute("""
        INSERT INTO invoices (client_id, project_id, invoice_number, amount, status, issue_date, due_date)
        VALUES (
            (SELECT client_id FROM projects WHERE id = ?),
            ?, ?, ?, ?, ?, ?
        )
    """, (
        project_id,
        project_id,
        fake.unique.bothify(text="INV-#####"),
        amount,
        random.choice(["sent", "paid", "overdue"]),
        random_date(180),
        random_date(30)
    ))
    invoice_ids.append(cursor.lastrowid)

#payments
for invoice_id in invoice_ids:
    if random.choice([True, False]):
        cursor.execute("""
            INSERT INTO payments (invoice_id, amount, payment_method, payment_date, reference)
            VALUES (?, ?, ?, ?, ?)
        """, (
            invoice_id,
            round(random.uniform(500, 15000), 2),
            random.choice(["bank_transfer", "credit_card", "cash"]),
            random_date(60),
            fake.uuid4()
        ))

#interactions
for _ in range(100):
    cursor.execute("""
        INSERT INTO interactions (client_id, user_id, type, summary)
        VALUES (?, ?, ?, ?)
    """, (
        random.choice(client_ids),
        random.choice(user_ids),
        random.choice(["call", "email", "meeting", "note"]),
        fake.sentence(nb_words=10)
    ))

#audit_logs
for _ in range(100):
    cursor.execute("""
        INSERT INTO audit_logs (user_id, entity, entity_id, action, old_value, new_value)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        random.choice(user_ids),
        random.choice(["client", "project", "invoice"]),
        random.randint(1, 50),
        random.choice(["create", "update", "delete"]),
        fake.word(),
        fake.word()
    ))

conn.commit()
conn.close()

print("Fake CRM data inserted successfully.")
