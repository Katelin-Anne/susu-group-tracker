"""Core business logic for a single rotating susu savings group."""
from dataclasses import dataclass, field
from .money import MoneyError, format_ghs, to_pesewas


class TrackerError(ValueError):
    """Raised when an operation violates the group's rules."""


@dataclass
class Member:
    name: str


@dataclass(frozen=True)
class Payout:
    week: int
    recipient: str
    amount_pesewas: int


@dataclass(frozen=True)
class WeekCloseResult:
    closed: bool
    week: int
    recipient: str | None = None
    amount_pesewas: int = 0
    owing: dict[str, int] = field(default_factory=dict)
    message: str = ""


class SusuGroup:
    """Manage contributions and payouts for one fixed-contribution group.

    Members are paid in join order. A group has one payout cycle, one payout
    per member. Members may be added only before the first contribution.
    """

    def __init__(self, weekly_contribution: str | int):
        amount = to_pesewas(weekly_contribution)
        if amount <= 0:
            raise TrackerError("Weekly contribution must be greater than zero.")
        self.weekly_contribution_pesewas = amount
        self.members: list[Member] = []
        self.current_week = 1
        self._payments: dict[int, dict[str, int]] = {1: {}}
        self.payout_history: list[Payout] = []

    def add_member(self, name: str) -> None:
        cleaned = name.strip() if isinstance(name, str) else ""
        if not cleaned:
            raise TrackerError("Member name or ID cannot be empty.")
        if self._has_any_contribution() or self.payout_history:
            raise TrackerError("Members can only be added before the first contribution.")
        if any(m.name.casefold() == cleaned.casefold() for m in self.members):
            raise TrackerError(f"Member '{cleaned}' already exists.")
        self.members.append(Member(cleaned))

    def record_contribution(self, member_name: str, amount: str | int) -> int:
        self._ensure_group_can_run()
        member = self._find_member(member_name)
        amount_pesewas = to_pesewas(amount)
        if amount_pesewas <= 0:
            raise TrackerError("Contribution amount must be greater than zero.")
        paid = self._payments.setdefault(self.current_week, {}).get(member.name, 0)
        remaining = self.weekly_contribution_pesewas - paid
        if amount_pesewas > remaining:
            raise TrackerError(
                f"Payment exceeds {member.name}'s remaining balance of {format_ghs(remaining)}."
            )
        self._payments[self.current_week][member.name] = paid + amount_pesewas
        return self.weekly_contribution_pesewas - (paid + amount_pesewas)

    def close_week(self) -> WeekCloseResult:
        self._ensure_group_can_run()
        week = self.current_week
        payments = self._payments.setdefault(week, {})
        owing = {
            member.name: self.weekly_contribution_pesewas - payments.get(member.name, 0)
            for member in self.members
            if payments.get(member.name, 0) < self.weekly_contribution_pesewas
        }
        if owing:
            details = ", ".join(f"{name} owes {format_ghs(amount)}" for name, amount in owing.items())
            return WeekCloseResult(False, week, owing=owing,
                                   message=f"Week {week} cannot close: {details}.")
        recipient = self.members[week - 1].name
        pot = self.weekly_contribution_pesewas * len(self.members)
        self.payout_history.append(Payout(week, recipient, pot))
        self.current_week += 1
        if self.current_week <= len(self.members):
            self._payments[self.current_week] = {}
        return WeekCloseResult(True, week, recipient, pot,
                               message=f"Week {week} closed. {recipient} receives {format_ghs(pot)}.")

    def report(self) -> dict:
        paid = self._payments.get(self.current_week, {}) if self.current_week <= len(self.members) else {}
        member_status = {}
        for member in self.members:
            amount_paid = paid.get(member.name, 0)
            remaining = self.weekly_contribution_pesewas - amount_paid
            member_status[member.name] = {
                "paid_pesewas": amount_paid,
                "owes_pesewas": max(0, remaining),
                "paid_in_full": amount_paid >= self.weekly_contribution_pesewas,
            }
        return {
            "current_week": self.current_week if self.current_week <= len(self.members) else None,
            "completed": bool(self.members) and len(self.payout_history) == len(self.members),
            "weekly_contribution_pesewas": self.weekly_contribution_pesewas,
            "members": member_status,
            "payout_history": list(self.payout_history),
        }

    def _find_member(self, name: str) -> Member:
        cleaned = name.strip() if isinstance(name, str) else ""
        for member in self.members:
            if member.name.casefold() == cleaned.casefold():
                return member
        raise TrackerError(f"Unknown member '{name}'.")

    def _has_any_contribution(self) -> bool:
        return any(amount > 0 for week in self._payments.values() for amount in week.values())

    def _ensure_group_can_run(self) -> None:
        if not self.members:
            raise TrackerError("Add at least one member before recording payments or closing a week.")
        if len(self.payout_history) >= len(self.members):
            raise TrackerError("This group's payout cycle is complete.")
