# Biblioteka promptów ról

Każdy plik jest samodzielnym promptem operacyjnym: określa misję, sposób pracy, wymagany rezultat i granice. Są celowo po angielsku, aby można je było bezpośrednio podawać modelom; nazwy plików są stabilnymi kluczami ról dla `python agent.py prompt-set`.

| Cel | Prompt |
| --- | --- |
| Koordynacja zadania i decyzje | `ceo.md` |
| Analiza kodu i wpływu zmian | `analyst.md` |
| Reguły domenowe i wymagania | `business.md` |
| Priorytety i discovery produktu | `product.md` |
| Projekt rozwiązania | `architect.md` |
| Implementacja | `developer.md` |
| Specyfikacja testów red-green-refactor | `tdd.md` |
| Niezależna walidacja jakości | `qa.md` |
| Przegląd zmian | `reviewer.md` |
| Testy przeglądarkowe/E2E | `browser.md` |
| Bezpieczeństwo aplikacji | `security.md` |
| Operacje i wdrożenia | `devops.md` |
| Dane, metryki i pipeline'y | `data.md` |
| Dokumentacja techniczna | `documentation.md` |
| Badania i synteza źródeł | `researcher.md` |

## Zasady użycia

1. Wybierz rolę według odpowiedzialności, nie według samego tytułu zadania.
2. Przekaż prompt razem z konkretnym celem, kryteriami akceptacji, zakresem repozytoriów i ograniczeniami.
3. Uprawnienia egzekwuj narzędziowo; prompt nie może ich rozszerzać.
4. Przy zmianie promptu utwórz nową wersję, sprawdź ją na reprezentatywnym zadaniu i zachowaj wynik wraz z wersją/modellem.
5. Łącz role sekwencyjnie: analiza lub produkt → architektura → TDD/development → review/security/QA → dokumentacja. CEO koordynuje tylko wtedy, gdy zadanie ma wiele zależności.
