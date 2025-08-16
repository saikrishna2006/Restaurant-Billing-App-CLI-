#!/usr/bin/env python3
"""
Restaurant Billing App (CLI)
--------------------------------
- Clean veg/non-veg menus
- Pick multiple items with quantities
- Auto-calculates totals + tax
- Generates a formatted receipt
- (Optional) email the receipt if SMTP is configured

Run:
    python restaurant_app.py
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# --- Configuration ---
BRAND = "Sai Krishna Restaurant"
CURRENCY = "₹"
TAX_RATE = 0.05  # 5% GST

MENUS: Dict[str, Dict[str, int]] = {
    "veg": {
        "Idli": 50,
        "Dosa": 50,
        "Veg Biryani": 100,
        "Chapathi": 50,
        "Parota": 50,
        "Pulihora": 50,
        "Veg Fried Rice": 100,
        "Veg Noodles": 100,
    },
    "nonveg": {
        "Chicken Idli": 100,
        "Chicken Dosa": 100,
        "Chicken Chapathi": 100,
        "Chicken Parota": 100,
        "Egg Fried Rice": 100,
        "Egg Noodles": 100,
        "Chicken Fried Rice": 299,
        "Chicken Noodles": 299,
        "Biryani": 299,
        "Dum Biryani": 299,
        "Mandi": 299,
        "String Biryani": 299,
        "Frontier Biryani": 299,
        "Chicken Lollipop": 299,
    },
}

# --- Data Models ---
@dataclass
class LineItem:
    name: str
    unit_price: int
    qty: int

    @property
    def total(self) -> int:
        return self.unit_price * self.qty

@dataclass
class Order:
    category: str
    items: List[LineItem]
    created_at: datetime

    @property
    def subtotal(self) -> int:
        return sum(it.total for it in self.items)

    @property
    def tax(self) -> float:
        return round(self.subtotal * TAX_RATE, 2)

    @property
    def grand_total(self) -> float:
        return round(self.subtotal + self.tax, 2)

# --- Helpers ---
def hr(char: str = "-", width: int = 72) -> str:
    return char * width

def ask(prompt: str) -> str:
    try:
        return input(prompt)
    except (KeyboardInterrupt, EOFError):
        print("\nExiting. Goodbye!")
        sys.exit(0)

def choose_category() -> str:
    while True:
        val = ask("Choose category [veg/nonveg]: ").strip().lower()
        if val in MENUS:
            return val
        print("Invalid choice. Please type 'veg' or 'nonveg'.")

def display_menu(category: str) -> List[Tuple[str, int, str]]:
    print(f"\n{BRAND} — {category.upper()} MENU")
    print(hr())
    print(f"{'Code':<6}{'Item':<28}{'Price':>10}")
    print(hr())
    code_rows: List[Tuple[str, int, str]] = []
    for idx, (name, price) in enumerate(MENUS[category].items(), start=1):
        code_str = f"{category[0].upper()}{idx:02d}"
        print(f"{code_str:<6}{name:<28}{CURRENCY}{price:>9}")
        code_rows.append((code_str, price, name))
    print(hr())
    return code_rows

def code_to_item(category: str, code_map: Dict[str, Tuple[str, int]]) -> Tuple[str, int]:
    while True:
        code = ask("Enter item code (or 'done' to finish): ").strip().upper()
        if code == "DONE":
            return ("", 0)
        if code in code_map:
            name, price = code_map[code]
            return (name, price)
        print("Invalid code. Please enter a valid item code.")

def ask_qty() -> int:
    while True:
        raw = ask("Enter quantity: ").strip()
        if raw.isdigit() and int(raw) > 0:
            return int(raw)
        print("Quantity must be a positive number.")

def build_code_map(category: str) -> Dict[str, Tuple[str, int]]:
    return {
        f"{category[0].upper()}{i:02d}": (name, price)
        for i, (name, price) in enumerate(MENUS[category].items(), start=1)
    }

def make_order() -> Order:
    print(f"Welcome to {BRAND}!")
    category = choose_category()
    display_menu(category)
    code_map = build_code_map(category)

    items: List[LineItem] = []
    while True:
        name, price = code_to_item(category, code_map)
        if not name:
            break
        qty = ask_qty()
        items.append(LineItem(name=name, unit_price=price, qty=qty))
        print(f"Added: {name} x{qty} — {CURRENCY}{price * qty}")
        print(hr())

    if not items:
        print("No items selected. Exiting.")
        sys.exit(0)

    return Order(category=category, items=items, created_at=datetime.now())

def render_receipt(order: Order, customer_name: Optional[str] = None, order_id: Optional[str] = None) -> str:
    if order_id is None:
        order_id = f"ORD-{order.created_at.strftime('%Y%m%d')}-{str(abs(hash(order.created_at)))[:6]}"
    title = f"{BRAND} — Receipt"
    header = [
        title,
        hr("="),
        f"Order ID : {order_id}",
        f"Date     : {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Category : {order.category.upper()}",
    ]
    if customer_name:
        header.append(f"Customer : {customer_name}")
    body = [
        hr(),
        f"{'Item':<28}{'Qty':>5}{'Rate':>10}{'Total':>12}",
        hr(),
    ]
    for it in order.items:
        body.append(f"{it.name:<28}{it.qty:>5}{CURRENCY}{it.unit_price:>9}{CURRENCY}{it.total:>11}")
    body.extend([
        hr(),
        f"{'Sub Total':<43}{CURRENCY}{order.subtotal:>11}",
        f"{'GST (5%)':<43}{CURRENCY}{order.tax:>11.2f}",
        hr(),
        f"{'Grand Total':<43}{CURRENCY}{order.grand_total:>11.2f}",
        hr("="),
        "Thank you for your order!",
    ])
    return "\n".join(header + body)

def save_receipt(text: str, filename: Optional[str] = None) -> str:
    if not filename:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"receipt_{stamp}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    return filename

# --- Main ---
def main():
    order = make_order()
    customer = ask("Enter customer name (optional): ").strip() or None
    receipt_text = render_receipt(order, customer_name=customer)
    print("\n" + receipt_text + "\n")
    # Save receipt
    fn = save_receipt(receipt_text)
    print(f"Receipt saved to: {fn}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCanceled by user.")
