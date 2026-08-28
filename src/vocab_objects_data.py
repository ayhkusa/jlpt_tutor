"""Compatibility view of canonical N4 household-object learning data."""

try:
	from .vocabulary_repository import load_household_objects
except ImportError:
	from vocabulary_repository import load_household_objects


HOUSEHOLD_OBJECTS = load_household_objects()