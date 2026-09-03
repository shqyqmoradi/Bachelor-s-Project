from __future__ import annotations

import unittest
from decimal import Decimal

from benchmark.config import Settings
from benchmark.data_generator import CanonicalGenerator


class GeneratorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.settings = Settings(seed=1234, orders=25, batch_size=7)

    def test_reproducible(self) -> None:
        a, b = CanonicalGenerator(self.settings), CanonicalGenerator(self.settings)
        self.assertEqual(a.customers(), b.customers())
        self.assertEqual(list(a.order_batches()), list(b.order_batches()))

    def test_counts_keys_and_money(self) -> None:
        g = CanonicalGenerator(self.settings)
        customers = g.customers()
        addresses = g.addresses()
        batches = list(g.order_batches())
        orders = [row for batch in batches for row in batch.orders]
        items = [row for batch in batches for row in batch.items]
        payments = [row for batch in batches for row in batch.payments]
        shipments = [row for batch in batches for row in batch.shipments]
        self.assertEqual(len(customers), self.settings.customer_count)
        self.assertEqual(len(addresses), self.settings.customer_count)
        self.assertEqual({row[0] for row in customers}, {row[1] for row in addresses})
        self.assertEqual(len(orders), self.settings.orders)
        self.assertEqual(len(payments), self.settings.orders)
        self.assertEqual(len(shipments), self.settings.orders)
        self.assertEqual(len({row[0] for row in orders}), len(orders))
        self.assertEqual(len({row[0] for row in items}), len(items))
        order_ids = {row[0] for row in orders}
        self.assertTrue(all(row[1] in order_ids for row in items))
        for order in orders:
            self.assertEqual(order[9], order[6] + order[7] - order[8])
            self.assertIsInstance(order[9], Decimal)
            self.assertEqual(order[9], order[9].quantize(Decimal("0.01")))
        self.assertTrue(all(1 <= row[3] <= 4 for row in items))

    def test_batch_bound(self) -> None:
        batches = list(CanonicalGenerator(self.settings).order_batches())
        self.assertTrue(all(1 <= len(batch.orders) <= self.settings.batch_size for batch in batches))


if __name__ == "__main__":
    unittest.main()
