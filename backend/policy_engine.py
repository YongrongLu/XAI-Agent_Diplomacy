from dataclasses import dataclass


@dataclass(frozen=True)
class Decision:
    status: str
    code: str
    explanation: str


def departure(time: str) -> Decision:
    if time < '09:30':
        return Decision('blocked', 'HARD_CONSTRAINT_VIOLATION', 'Carol requires group departures at or after 09:30.')
    return Decision('allowed', 'GROUP_DEPARTURE_ALLOWED', 'Departure respects Carol’s 09:30 boundary.')


def disclosure(field: str) -> Decision:
    if field != 'availability':
        return Decision('blocked', 'PRIVATE_DISCLOSURE_BLOCKED', 'Only availability may be shared; the underlying reason stays local.')
    return Decision('allowed', 'MINIMAL_DISCLOSURE', 'Only the availability signal may enter the shared feed.')


def contribution(extra: int) -> Decision:
    if extra < 0:
        return Decision('blocked', 'INVALID_AMOUNT', 'Extra contribution cannot be negative.')
    if extra > 100:
        return Decision('approval_required', 'DELEGATION_LIMIT', 'Alice must approve this exact additional contribution once.')
    return Decision('allowed', 'WITHIN_DELEGATION', 'The additional contribution is within Alice’s $100 delegation limit.')
