# Task 1: Rozbudować bibliotekę promptów ról: ujednolicić istniejące i dodać brakujące specjalizacje.

Status: complete

## Requirements
- Rozszerzyć sześć istniejących promptów bez zmiany ich nazw.
- Dodać role pokrywające brakujące etapy: produkt, architektura, implementacja, review, bezpieczeństwo, operacje, dane, dokumentacja i research.
- Dodać indeks opisujący przeznaczenie oraz bezpieczne użycie ról.

## Acceptance criteria
- W katalogu `prompts/` jest 15 samodzielnych promptów ról i indeks `README.md`.
- Każdy prompt ma misję, metodę pracy, rezultat i ograniczenia.
- Istniejące nazwy: analyst, browser, business, ceo, qa, tdd pozostają zachowane.

## Affected repositories
- universal-agent-workspace-v3

## TDD evidence
- Red: not applicable (Markdown prompt library)
- Green: 15 prompt files passed structural validation (Mission, Operating method, Deliverable, Guardrails).
- Regression: `python -m unittest discover -s tests -v` — 12 tests passed.

## Decisions and risks
- Prompty kierują zachowaniem modeli, ale nie zastępują egzekwowania uprawnień przez narzędzia i kod.
- Quality gate `TASK-1`: passed (unit, integration, regression evidence recorded).
