import unittest
from susu_tracker import SusuGroup, TrackerError
from susu_tracker.money import MoneyError, to_pesewas, format_ghs


class SusuGroupTests(unittest.TestCase):
    def setUp(self):
        self.group = SusuGroup("50.00")
        for name in ("Ama", "Kofi", "Esi"):
            self.group.add_member(name)

    def test_partial_payment_accumulates(self):
        self.group.record_contribution("Esi", "30.00")
        remaining = self.group.record_contribution("Esi", "20.00")
        self.assertEqual(remaining, 0)
        self.assertTrue(self.group.report()["members"]["Esi"]["paid_in_full"])

    def test_week_cannot_close_when_member_owes(self):
        self.group.record_contribution("Ama", "50.00")
        self.group.record_contribution("Kofi", "50.00")
        self.group.record_contribution("Esi", "30.00")
        result = self.group.close_week()
        self.assertFalse(result.closed)
        self.assertEqual(result.owing, {"Esi": 2000})
        self.assertEqual(self.group.current_week, 1)
        self.assertEqual(self.group.payout_history, [])

    def test_successful_close_pays_first_member_in_join_order(self):
        for name in ("Ama", "Kofi", "Esi"):
            self.group.record_contribution(name, "50.00")
        result = self.group.close_week()
        self.assertTrue(result.closed)
        self.assertEqual(result.recipient, "Ama")
        self.assertEqual(result.amount_pesewas, 15000)
        self.assertEqual(self.group.current_week, 2)

    def test_unknown_member_is_rejected(self):
        with self.assertRaises(TrackerError):
            self.group.record_contribution("Yaw", "10.00")

    def test_duplicate_member_is_rejected_case_insensitively(self):
        with self.assertRaises(TrackerError):
            self.group.add_member("ama")

    def test_zero_and_negative_payments_are_rejected(self):
        for amount in ("0", "-1.00"):
            with self.subTest(amount=amount), self.assertRaises(TrackerError):
                self.group.record_contribution("Ama", amount)

    def test_overpayment_is_rejected(self):
        self.group.record_contribution("Ama", "40.00")
        with self.assertRaises(TrackerError):
            self.group.record_contribution("Ama", "10.01")

    def test_money_is_exact_and_formatted_to_two_places(self):
        self.assertEqual(to_pesewas("0.10") + to_pesewas("0.20"), 30)
        self.assertEqual(format_ghs(30), "GHS 0.30")
        with self.assertRaises(MoneyError):
            to_pesewas("1.001")

    def test_members_cannot_be_added_after_contributions_begin(self):
        self.group.record_contribution("Ama", "1.00")
        with self.assertRaises(TrackerError):
            self.group.add_member("Yaw")

    def test_payout_rotation_and_cycle_completion(self):
        expected = [("Ama", 1), ("Kofi", 2), ("Esi", 3)]
        for expected_name, expected_week in expected:
            for name in ("Ama", "Kofi", "Esi"):
                self.group.record_contribution(name, "50.00")
            result = self.group.close_week()
            self.assertEqual((result.recipient, result.week), (expected_name, expected_week))
        self.assertTrue(self.group.report()["completed"])
        with self.assertRaises(TrackerError):
            self.group.close_week()

    def test_empty_group_cannot_close_week(self):
        group = SusuGroup("50.00")
        with self.assertRaises(TrackerError):
            group.close_week()


if __name__ == "__main__":
    unittest.main()
