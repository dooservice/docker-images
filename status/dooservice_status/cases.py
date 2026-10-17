"""What can be happening at an address, and what its page says about it."""

from dataclasses import dataclass
from enum import StrEnum


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


@dataclass(frozen=True)
class Wording:
    label: str
    title: str
    text: str
    final: bool = False


WORDING = {
    Case.CREATING: Wording(
        "Setting up",
        "This Odoo is being set up",
        "The database and apps are being created. You will be taken in as soon as it is ready.",
    ),
    Case.UPDATING: Wording(
        "Updating",
        "Updating this Odoo",
        "A new version is being applied. It will be back in a few minutes and you will be taken in.",
    ),
    Case.RESTORING: Wording(
        "Restoring",
        "Restoring the data",
        "The data is being restored from a backup. You will be taken in when it is done.",
    ),
    Case.STARTING: Wording(
        "Starting",
        "Starting…",
        "Odoo is starting. This usually takes less than a minute.",
    ),
    Case.MAINTENANCE: Wording(
        "Maintenance",
        "Scheduled maintenance",
        "The server is being updated. It will be back in a few minutes and you will be taken in.",
    ),
    Case.NOT_RESPONDING: Wording(
        "Not responding",
        "This Odoo is not responding",
        "This is usually temporary. This page keeps retrying and takes you in when it answers.",
    ),
    Case.FAILING: Wording(
        "Having a problem",
        "This Odoo ran into a problem",
        "Its team has been told. This page keeps retrying and takes you in as soon as it works again.",
    ),
    Case.VERIFYING_DOMAIN: Wording(
        "Preparing the domain",
        "Preparing this address",
        "This domain is new and its certificate is being issued. This usually takes a few minutes.",
    ),
    Case.STOPPED: Wording(
        "Stopped",
        "This Odoo is stopped",
        "It was stopped by its administrators. If you need it, contact them.",
        final=True,
    ),
    Case.EXPIRED: Wording(
        "Expired",
        "This copy no longer exists",
        "It was a temporary test copy and was removed when it expired. Ask for a new one if you need it.",
        final=True,
    ),
    Case.UNKNOWN: Wording(
        "Page not found",
        "There is no Odoo at this address",
        "Check that the address is spelled correctly.",
        final=True,
    ),
}
