# Susu Group Tracker

A small Python command-line application for managing one rotating susu savings group. It records weekly contributions, permits partial payments, prevents invalid payments, closes only fully paid weeks, pays members in joining order, and shows payout history.

## Requirements

- Python 3.10 or newer
- No third-party packages required

## Run the program

From the repository root:

```bash
python main.py
```

Enter the fixed weekly contribution in GHS, add members in the order they should receive payouts, then use the menu to record payments, close the week, or view the report.

## Run automated tests

```bash
python -m unittest discover -s tests -v
```

The tests cover partial payments, incomplete weeks, payout order and amount, unknown and duplicate members, invalid amounts, overpayments, exact money handling, membership rules, and the end of the payout cycle.

## Money representation

All money is converted to integer pesewas (100 pesewas = GHS 1.00). The program does not use binary floating-point values for financial calculations.
