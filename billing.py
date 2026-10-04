"""
Shop Billing System with Discount
---------------------------------
Rules:
  * Amount >= 500        -> ask for membership: member 20%, non-member 10%
  * Amount 200 to 499.99 -> ask for coupon:     valid coupon 5%, else 0%
  * Amount < 200         -> no discount

Features: input validation, member/coupon verification, one-time coupons,
bill numbers, optional GST, bill saving to a CSV file, daily summary.
"""

import csv
import os
from datetime import datetime

# ---------------- SETTINGS (change these as needed) ----------------
STORE_NAME = "MY SHOP"
GST_RATE = 0.0                    # e.g. set 5, 12 or 18 to add GST; 0 = no GST
BILL_FILE = "bills.csv"

MEMBER_DISCOUNT = 20
NON_MEMBER_DISCOUNT = 10
COUPON_DISCOUNT = 5
HIGH_LIMIT = 500
MID_LIMIT = 200

# Sample data. In a real shop this would come from a file or database.
MEMBER_IDS = {"M101", "M102", "M103"}
VALID_COUPONS = {"SAVE5", "FEST5", "NEW5"}
# -------------------------------------------------------------------


def ask_yes_no(question):
    """Keep asking until the cashier types yes/no (or y/n)."""
    while True:
        answer = input(question + " (yes/no): ").strip().lower()
        if answer in ("yes", "y"):
            return True
        if answer in ("no", "n"):
            return False
        print("  Please type 'yes' or 'no'.")


def get_amount():
    """Return a valid positive amount, or None when the cashier wants to exit."""
    while True:
        text = input("\nEnter purchase amount in Rs (or 'q' to close): ").strip()
        if text.lower() in ("q", "quit", "exit"):
            return None
        try:
            amount = float(text.replace(",", ""))
        except ValueError:
            print("  Invalid input! Enter a number such as 450 or 1299.50")
            continue
        if amount <= 0:
            print("  Amount must be greater than zero.")
            continue
        if amount > 10_000_000:
            print("  Amount looks too large. Please re-check.")
            continue
        return round(amount, 2)


def check_member():
    """Ask if member; verify the member ID. Returns True only if verified."""
    if not ask_yes_no("Is the customer a member?"):
        return False
    member_id = input("  Enter member ID: ").strip().upper()
    if member_id in MEMBER_IDS:
        print("  Member verified.")
        return True
    print("  Member ID not found. Treated as non-member.")
    return False


def check_coupon():
    """Ask for coupon; verify the code and make it one-time use."""
    if not ask_yes_no("Does the customer have a coupon code?"):
        return False
    code = input("  Enter coupon code: ").strip().upper()
    if code in VALID_COUPONS:
        VALID_COUPONS.remove(code)          # one-time use
        print("  Coupon accepted.")
        return True
    print("  Invalid or already used coupon. No discount.")
    return False


def get_discount_percent(amount):
    """Apply the discount rules and return (percent, reason)."""
    if amount >= HIGH_LIMIT:
        if check_member():
            return MEMBER_DISCOUNT, "Member"
        return NON_MEMBER_DISCOUNT, "Non-member"
    if amount >= MID_LIMIT:
        if check_coupon():
            return COUPON_DISCOUNT, "Coupon"
        return 0, "No coupon"
    return 0, "Below Rs 200"


def save_bill(row):
    """Append the bill to a CSV file (creates header if file is new)."""
    header = ["Bill No", "Date", "Time", "Amount", "Discount %", "Reason",
              "Discount Amt", "GST", "Total Paid"]
    new_file = not os.path.exists(BILL_FILE)
    try:
        with open(BILL_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if new_file:
                writer.writerow(header)
            writer.writerow(row)
    except OSError:
        print("  Warning: could not save the bill to file!")


def next_bill_number():
    """Continue numbering from the last saved bill (so it survives restarts)."""
    if not os.path.exists(BILL_FILE):
        return 1
    try:
        with open(BILL_FILE, newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        return int(rows[-1][0]) + 1 if len(rows) > 1 else 1
    except (OSError, ValueError, IndexError):
        return 1


def print_bill(bill_no, now, amount, percent, reason, disc_amt, gst, total):
    line = "=" * 36
    print("\n" + line)
    print(STORE_NAME.center(36))
    print(line)
    print(f"Bill No : {bill_no:<10} {now:%d-%m-%Y %H:%M}")
    print("-" * 36)
    print(f"Purchase Amount   : Rs {amount:>10,.2f}")
    print(f"{'Discount ' + str(percent) + '%':<18}: -Rs {disc_amt:>9,.2f}")
    print(f"  ({reason})")
    if GST_RATE > 0:
        print(f"GST @ {GST_RATE}%".ljust(18) + f": Rs {gst:>10,.2f}")
    print("-" * 36)
    print(f"AMOUNT TO PAY     : Rs {total:>10,.2f}")
    print(line)
    print("Thank you! Visit again.".center(36))


def main():
    bill_no = next_bill_number()
    count = 0
    sales = 0.0
    total_discount = 0.0

    print(f"===== {STORE_NAME} BILLING SYSTEM =====")

    while True:
        amount = get_amount()
        if amount is None:
            break

        percent, reason = get_discount_percent(amount)
        disc_amt = round(amount * percent / 100, 2)
        taxable = amount - disc_amt
        gst = round(taxable * GST_RATE / 100, 2)
        total = round(taxable + gst, 2)

        now = datetime.now()
        print_bill(bill_no, now, amount, percent, reason, disc_amt, gst, total)
        save_bill([bill_no, now.strftime("%d-%m-%Y"), now.strftime("%H:%M:%S"),
                   amount, percent, reason, disc_amt, gst, total])

        count += 1
        sales += total
        total_discount += disc_amt
        bill_no += 1

    print("\n" + "=" * 36)
    print("DAY SUMMARY".center(36))
    print("=" * 36)
    print(f"Bills generated  : {count}")
    print(f"Total discount   : Rs {total_discount:,.2f}")
    print(f"Total collection : Rs {sales:,.2f}")
    print(f"Bills saved in   : {BILL_FILE}")
    print("=" * 36)


if __name__ == "__main__":
    main()
