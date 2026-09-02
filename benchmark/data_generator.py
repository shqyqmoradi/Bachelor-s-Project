from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterator

from .config import Settings

MONEY = Decimal("0.01")
BASE_DATE = datetime(2022, 1, 1, tzinfo=timezone.utc)
FIRST = ("Liam", "Emma", "Noah", "Olivia", "Ethan", "Mia", "Lucas", "Sophia", "Amir", "Sara", "Arman", "Nora")
LAST = ("Smith", "Martin", "Garcia", "Brown", "Wilson", "Taylor", "Rahimi", "Karimi", "Dubois", "Bernard")
CITIES = (("Paris", "75001", "FR"), ("Lyon", "69001", "FR"), ("Berlin", "10115", "DE"), ("Madrid", "28001", "ES"), ("Rome", "00118", "IT"), ("Toronto", "M5H2N2", "CA"))
ORDER_STATUSES = ("pending", "paid", "processing", "shipped", "delivered", "cancelled")
PAYMENT_METHODS = ("card", "paypal", "bank_transfer", "cash_on_delivery")


def money(value: Decimal | float | int | str) -> Decimal:
    return Decimal(str(value)).quantize(MONEY, rounding=ROUND_HALF_UP)


def product_price(product_id: int) -> Decimal:
    return money(5 + ((product_id * 7919) % 49_500) / 100)


@dataclass
class OrderBatch:
    orders: list[tuple]
    items: list[tuple]
    payments: list[tuple]
    shipments: list[tuple]


class CanonicalGenerator:
    """Pure ID-derived generator: the same seed and scale always produce identical rows."""

    def __init__(self, settings: Settings):
        self.s = settings

    def categories(self) -> list[tuple]:
        return [(i, f"Category {i:02d}", f"Curated products in category {i:02d}") for i in range(1, self.s.category_count + 1)]

    def customers(self) -> list[tuple]:
        rows = []
        for i in range(1, self.s.customer_count + 1):
            first, last = FIRST[i % len(FIRST)], LAST[(i * 7) % len(LAST)]
            rows.append((i, first, last, f"{first}.{last}.{i}@example.test".lower(), f"+33-6-{i % 10_000_000:07d}", BASE_DATE + timedelta(minutes=i), True))
        return rows

    def addresses(self) -> list[tuple]:
        rows = []
        for i in range(1, self.s.customer_count + 1):
            city, postal, country = CITIES[i % len(CITIES)]
            rows.append((i, i, "Home", f"{1 + i % 999} Market Street", None, city, None, postal, country, True))
        return rows

    def products(self) -> list[tuple]:
        return [(i, 1 + (i - 1) % self.s.category_count, f"SKU-{i:09d}", f"Product {i:09d}", f"Realistic catalog item {i}", product_price(i), (i * 37) % 1000, True, BASE_DATE + timedelta(minutes=i)) for i in range(1, self.s.product_count + 1)]

    def order_batches(self) -> Iterator[OrderBatch]:
        batch = OrderBatch([], [], [], [])
        item_id = 0
        for order_id in range(1, self.s.orders + 1):
            rng = random.Random(self.s.seed + order_id)
            customer_id = 1 + rng.randrange(self.s.customer_count)
            order_date = BASE_DATE + timedelta(seconds=rng.randrange(0, 4 * 365 * 24 * 3600))
            status = ORDER_STATUSES[rng.choices(range(6), weights=(5, 12, 12, 15, 52, 4), k=1)[0]]
            chosen = rng.sample(range(1, self.s.product_count + 1), k=rng.randint(1, min(5, self.s.product_count)))
            order_items, subtotal = [], Decimal("0")
            for product_id in chosen:
                item_id += 1
                qty = rng.randint(1, 4)
                unit = product_price(product_id)
                discount = money(unit * qty * Decimal("0.05")) if rng.random() < 0.15 else Decimal("0.00")
                line = money(unit * qty - discount)
                subtotal += line
                order_items.append((item_id, order_id, product_id, qty, unit, discount, line))
            shipping = Decimal("0.00") if subtotal >= 100 else Decimal("7.50")
            order_discount = money(subtotal * Decimal("0.03")) if rng.random() < 0.1 else Decimal("0.00")
            total = money(subtotal + shipping - order_discount)
            batch.orders.append((order_id, customer_id, customer_id, order_date, status, "USD", money(subtotal), shipping, order_discount, total))
            batch.items.extend(order_items)
            payment_status = "failed" if status == "cancelled" else ("pending" if status == "pending" else "paid")
            paid_at = None if payment_status in ("failed", "pending") else order_date + timedelta(minutes=2)
            batch.payments.append((order_id, order_id, PAYMENT_METHODS[order_id % 4], payment_status, total, f"TX-{order_id:012d}", paid_at))
            shipment_status = {"pending":"pending", "paid":"packed", "processing":"packed", "shipped":"shipped", "delivered":"delivered", "cancelled":"returned"}[status]
            shipped_at = order_date + timedelta(days=1) if shipment_status in ("shipped", "delivered") else None
            delivered_at = shipped_at + timedelta(days=3) if shipment_status == "delivered" else None
            tracking = f"TRK-{order_id:012d}" if shipped_at else None
            batch.shipments.append((order_id, order_id, "ParcelCo" if shipped_at else None, tracking, shipment_status, shipped_at, delivered_at))
            if len(batch.orders) >= self.s.batch_size:
                yield batch
                batch = OrderBatch([], [], [], [])
        if batch.orders:
            yield batch

    @staticmethod
    def mongo_customer(customer: tuple, address: tuple) -> dict:
        return {"_id": customer[0], "firstName": customer[1], "lastName": customer[2], "email": customer[3], "phone": customer[4], "createdAt": customer[5], "isActive": customer[6], "addresses": [{"addressId": address[0], "label": address[2], "line1": address[3], "line2": address[4], "city": address[5], "stateProvince": address[6], "postalCode": address[7], "countryCode": address[8], "isDefault": address[9]}]}

    @staticmethod
    def mongo_order(order: tuple, items: list[tuple], payment: tuple, shipment: tuple) -> dict:
        address_id = order[2]
        city, postal, country = CITIES[address_id % len(CITIES)]
        address_snapshot = {"addressId": address_id, "label": "Home", "line1": f"{1 + address_id % 999} Market Street", "line2": None, "city": city, "stateProvince": None, "postalCode": postal, "countryCode": country}
        return {"_id": order[0], "customerId": order[1], "shippingAddress": address_snapshot, "orderDate": order[3], "status": order[4], "currency": order[5], "subtotal": order[6], "shippingAmount": order[7], "discountAmount": order[8], "totalAmount": order[9], "items": [{"orderItemId": i[0], "productId": i[2], "productName": f"Product {i[2]:09d}", "quantity": i[3], "unitPrice": i[4], "discountAmount": i[5], "lineTotal": i[6]} for i in items], "payment": {"paymentId": payment[0], "method": payment[2], "status": payment[3], "amount": payment[4], "transactionRef": payment[5], "paidAt": payment[6]}, "shipment": {"shipmentId": shipment[0], "carrier": shipment[2], "trackingNumber": shipment[3], "status": shipment[4], "shippedAt": shipment[5], "deliveredAt": shipment[6]}}
