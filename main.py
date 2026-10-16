"""Simple menu-driven command-line interface for the Susu Group Tracker."""
from susu_tracker import SusuGroup, TrackerError, MoneyError
from susu_tracker.money import format_ghs


def print_report(group: SusuGroup) -> None:
    report = group.report()
    print("\n=== Susu Group Report ===")
    if report["completed"]:
        print("Current week: Group cycle complete")
    else:
        print(f"Current week: {report['current_week']}")
    print(f"Weekly contribution: {format_ghs(report['weekly_contribution_pesewas'])}")
    print("Members:")
    for name, status in report["members"].items():
        state = "PAID IN FULL" if status["paid_in_full"] else f"OWES {format_ghs(status['owes_pesewas'])}"
        print(f"  - {name}: paid {format_ghs(status['paid_pesewas'])}; {state}")
    print("Payout history:")
    if not report["payout_history"]:
        print("  (none yet)")
    for payout in report["payout_history"]:
        print(f"  - Week {payout.week}: {payout.recipient} received {format_ghs(payout.amount_pesewas)}")
    print()


def main() -> None:
    print("Susu Group Tracker")
    while True:
        try:
            amount = input("Fixed weekly contribution in GHS (e.g. 50.00): ").strip()
            group = SusuGroup(amount)
            break
        except (TrackerError, MoneyError) as exc:
            print(f"Error: {exc}")
    print("Add members in payout order. Enter a blank name when finished.")
    while True:
        name = input("Member name/ID: ")
        if not name.strip():
            break
        try:
            group.add_member(name)
            print(f"Added {name.strip()}.")
        except TrackerError as exc:
            print(f"Error: {exc}")
    while True:
        print("\n1. Add member  2. Record contribution  3. Close week  4. Show report  5. Quit")
        choice = input("Choose an option: ").strip()
        try:
            if choice == "1":
                group.add_member(input("Member name/ID: "))
                print("Member added.")
            elif choice == "2":
                name = input("Member name/ID: ")
                amount = input("Payment amount in GHS: ")
                remaining = group.record_contribution(name, amount)
                print(f"Payment recorded. Remaining balance: {format_ghs(remaining)}")
            elif choice == "3":
                result = group.close_week()
                print(result.message)
            elif choice == "4":
                print_report(group)
            elif choice == "5":
                print("Goodbye.")
                return
            else:
                print("Choose a number from 1 to 5.")
        except (TrackerError, MoneyError) as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    main()
