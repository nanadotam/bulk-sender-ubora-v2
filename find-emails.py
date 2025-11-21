import pandas as pd
import smtplib

# -----------------------
# CONFIG
# -----------------------
DOMAIN = "ashesi.edu.gh"
INPUT_CSV = "C2029A-Names-students.csv"
OUTPUT_CSV = "2029-emails.csv"

# -----------------------
# Helpers
# -----------------------
def normalize(s):
    """Lowercase and strip only."""
    return str(s).strip().lower() if pd.notna(s) else ""

def no_space_lower(s):
    """Lowercase, strip, remove excess internal spaces but preserve hyphens."""
    return "-".join(["".join(part.split()) for part in s.split("-")]).lower()


# -----------------------
# Generate ONLY the valid Ashesi patterns:
# 1. firstname.lastname
# 2. middle.lastname (for each middle)
# -----------------------
def generate_ashesi_emails(first, middle, last):

    # sanitize inputs
    first_raw = normalize(first)
    middle_raw = normalize(middle)
    last_raw = normalize(last)

    # last name MUST keep hyphens but remove extra internal spaces
    last_clean = no_space_lower(last_raw)

    emails = set()

    # Extract ONLY the first token of first name(s)
    first_token = first_raw.split()[0] if first_raw else ""

    # --- 1. firstname.lastname ---
    if first_token and last_clean:
        emails.add(f"{first_token}.{last_clean}@{DOMAIN}")

    # --- 2. middle.lastname for EACH middle name ---
    if middle_raw and last_clean:
        middle_parts = [m.strip() for m in middle_raw.split() if m.strip()]
        for m in middle_parts:
            emails.add(f"{m}.{last_clean}@{DOMAIN}")

    return list(emails)


# -----------------------
# Authenticated SMTP Ping (Outlook)
# ⚠ Note: Office365 may return 250 for invalid addresses.
# Treat this as a heuristic, not guaranteed verification.
# -----------------------
def authenticated_smtp_check(guess_email, outlook_email, outlook_password):
    try:
        smtp_server = "smtp.office365.com"
        port = 587

        server = smtplib.SMTP(smtp_server, port, timeout=10)
        server.starttls()
        server.login(outlook_email, outlook_password)

        server.mail(outlook_email)
        code, response = server.rcpt(guess_email)
        server.quit()

        return code == 250 or code == 251
    except Exception as e:
        print(f"⚠️ Error checking {guess_email}: {e}")
        return False


# -----------------------
# Main Enrichment Function
# -----------------------
def enrich_emails_with_auth_ping(input_csv, output_csv, outlook_email, outlook_password):
    df = pd.read_csv(input_csv)
    df.fillna("", inplace=True)

    # Ensure Email column exists
    if "Email" not in df.columns:
        df["Email"] = ""

    for idx, row in df.iterrows():

        current_email = str(row["Email"]).strip().lower()

        first = row.get("First Name(s)", "")
        middle = row.get("Middle Name", "")
        last = row.get("Family name(s)", "")

        # Only generate if Email is empty
        if current_email in ["", "nan", "none"]:
            guesses = generate_ashesi_emails(first, middle, last)

            for guess in guesses:
                print(f"🔍 Trying: {guess}")
                if authenticated_smtp_check(guess, outlook_email, outlook_password):
                    print(f"✅ Valid email (heuristic): {guess}")
                    df.at[idx, "Email"] = guess
                    break
            else:
                print(f"❌ No match for: {first} {middle} {last}")

    df.to_csv(output_csv, index=False)
    print(f"\n✅ Enriched file saved to: {output_csv}")


# -----------------------
# Run it
# -----------------------
if __name__ == "__main__":
    print("🔐 Outlook Login Required")
    outlook_email = input("Your Ashesi Outlook Email: ").strip()
    outlook_password = input("Your Outlook Password (visible as you type): ").strip()

    enrich_emails_with_auth_ping(INPUT_CSV, OUTPUT_CSV, outlook_email, outlook_password)
