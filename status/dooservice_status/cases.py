"""What can be happening at an address. What its page says about it is in dooservice/locales,
under `cases.<case>` of `status.json`."""

from enum import StrEnum

from .constants import FINAL_CASES


class Case(StrEnum):
    CREATING = "creating"
    UPDATING = "updating"
    RESTORING = "restoring"
    STARTING = "starting"
    MAINTENANCE = "maintenance"
    NOT_RESPONDING = "not_responding"
    FAILING = "failing"
    VERIFYING_DOMAIN = "verifying_domain"
    STOPPED = "stopped"
    EXPIRED = "expired"
    UNKNOWN = "unknown"

    @property
    def final(self) -> bool:
        """Nothing moves it on by itself: somebody has to start the environment again."""
        return self.value in FINAL_CASES
