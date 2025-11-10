from bisect import bisect_right, insort
from typing import Any, Optional, List

class TimeFloorSchedule:
    """
    Eine einfache zeitbasierte Planungsstruktur für zukünftige Zustände.

    Diese Klasse speichert Paare aus (Zeitpunkt, Zustand) in aufsteigender Reihenfolge.
    Sie erlaubt das Einfügen geplanter Zustände für zukünftige Zeitpunkte
    und das spätere Abrufen des zuletzt gültigen Zustands (d. h. des Zustands
    mit dem größten Zeitpunkt, der kleiner oder gleich dem aktuellen Zeitpunkt ist).

    Beim Abrufen werden alle älteren Einträge automatisch gelöscht,
    sodass nur zukünftige Zustände erhalten bleiben.

    Beispiel:
        >>> sched = TimeFloorSchedule()
        >>> sched.put(22, 5)
        >>> sched.put(25, 7)
        >>> sched.put(27, 3)
        >>> sched.consume(23)
        5
        >>> sched.consume(28)
        3  # Der Zustand 7° bei t=25 wurde übersprungen

    Verwendungszweck:
        - Planung zukünftiger Sollwerte oder Befehle
        - Asynchrone Verarbeitung mit Zeitversatz
        - Automatisches Verwerfen veralteter Zustände
    """

    def __init__(self):
        """Initialisiert eine leere, zeitlich sortierte Struktur."""
        self._times: List[float] = []
        self._values: List[Any] = []

    def put(self, t: float, state: Any) -> None:
        """
        Fügt einen neuen Zustand für den gegebenen Zeitpunkt ein.

        Args:
            t: Zeitpunkt (z. B. Sekunden oder Timestamp)
            state: Beliebiger zu speichernder Zustand
        """
        i = bisect_right(self._times, t)
        insort(self._times, t)
        self._values.insert(i, state)

    def consume(self, now: float) -> Optional[Any]:
        """
        Gibt den zuletzt fälligen Zustand (<= now) zurück und löscht alle älteren Einträge.

        Args:
            now: Aktueller Zeitpunkt
        Returns:
            Der zuletzt gültige Zustand oder None, falls kein Eintrag fällig ist.
        """
        cut = bisect_right(self._times, now)
        if cut == 0:
            return None
        result = self._values[cut - 1]
        del self._times[:cut]
        del self._values[:cut]
        return result

    def peek(self, now: float) -> Optional[Any]:
        """
        Gibt den zuletzt fälligen Zustand (<= now) zurück, ohne Einträge zu löschen.

        Args:
            now: Aktueller Zeitpunkt
        Returns:
            Der zuletzt gültige Zustand oder None, falls kein Eintrag fällig ist.
        """
        cut = bisect_right(self._times, now)
        return None if cut == 0 else self._values[cut - 1]