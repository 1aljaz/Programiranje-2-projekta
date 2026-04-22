# Repozitorij za projekt pri Programiranju 2
### Fakulteta za matematiko in fiziko, Univerza v Ljubljani
#### Program Aplikativna matematika 2. letnik

# Opis projekta
Modularen cevovod v Pythonu, ki sprempla Google Trends za 20 držav. Sistem beleži globalni obseg iskanja,
shranjuje ygodovinske podatke o prometu in uporablja statistično analizo za zaznavanje ter vizualizacijo
anomalij v prometu.

# Struktura
Projekt je razdeljen na več modulov za boljšo preglednost:
* **`main.py`**: Glavni upravljalnik, ki vodi cikel pridobivanja, shranjevanja in prikaza podatkov.
* **`fetch.py`**: Skrbi za RSS zahteve na Google Trends za 20 regij.
* **`parse.py`**: Čisti in pretvarja surove XML podatke v strukturirane objekte.
* **`logic.py`**: Vsebuje algoritem za zaznavanje skokov na podlagi mediane.
* **`graphs.py`**: Upravlja `matplotlib` vizualizacije in formatiranje časovnih osi.
* **`read.py` / `write.py`**: Modula za upravljanje branja in pisanja v CSV datoteke.
* **`settings.py`**: Centralizirana konfiguracija za prag skoka (`SPIKE_THRESHOLD`) in seznam držav.

# Namestitev
**Kloniraj repozitorij**:
    ```bash
    git clone <url-tvojega-repozitorija>
    cd Python
    ```

**Nastavi virtualno okolje**:
    ```powershell
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    ```

**Namesti knjižnice**:
    ```bash
    pip install -r requirements.txt
    ```

# Uporaba

Posodobi `hourly_traffic.csv` in zabeleži nove trende v `top_searches.csv`, če so se ti spremenili.
```bash
python main.py
