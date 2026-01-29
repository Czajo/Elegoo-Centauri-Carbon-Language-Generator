# ELEGOO Translation Tool by Czajo

Narzędzie do tłumaczenia interfejsu drukarek 3D ELEGOO Centauri Carbon. Umożliwia pobieranie, edycję, tłumaczenie i wgrywanie plików tłumaczeń zarówno dla interfejsu ekranu dotykowego (UI), jak i interfejsu webowego drukarki.

## 📋 Spis treści

- [Funkcje](#funkcje)
- [Wymagania](#wymagania)
- [Instalacja](#instalacja)
- [Konfiguracja](#konfiguracja)
- [Użycie](#użycie)
- [Szczegółowy opis opcji](#szczegółowy-opis-opcji)
- [Struktura plików](#struktura-plików)
- [Rozwiązywanie problemów](#rozwiązywanie-problemów)
- [Informacje techniczne](#informacje-techniczne)
- [Bezpieczeństwo](#bezpieczeństwo)
- [Autor](#autor)

## 🚀 Funkcje

- ✅ Pobieranie plików tłumaczeń z drukarki przez SSH
- ✅ Automatyczne tłumaczenie przy użyciu Google Translate
- ✅ Ręczna edycja tłumaczeń
- ✅ Zastępowanie istniejących języków
- ✅ Dodawanie nowych języków
- ✅ Konwersja między formatami CSV i BIN
- ✅ Tłumaczenie interfejsu webowego (JSON)
- ✅ Modyfikacja przycisku wyboru języka w interfejsie webowym
- ✅ Wgrywanie plików z powrotem na drukarkę
- ✅ Restart drukarki przez SSH
- ✅ Narzędzia diagnostyczne
- ✅ Kolorowe komunikaty dla lepszej czytelności
- ✅ Automatyczne zapamiętywanie adresu IP drukarki

## 📦 Wymagania

### Wymagania systemowe

- Python 3.6 lub nowszy
- System operacyjny: Windows, Linux, macOS
- Połączenie sieciowe z drukarką ELEGOO

### Wymagane biblioteki Python
- `paramiko` - do połączeń SSH z drukarką
- `deep-translator` - do automatycznego tłumaczenia
- `colorama` - do kolorowych komunikatów (opcjonalne, ale zalecane)

### Wymagania dotyczące drukarki
- Drukarka ELEGOO z wgranym otwartym firmware **OpenCentauri** ([dokumentacja](https://docs.opencentauri.cc))
- Drukarka z włączonym SSH
- Domyślne dane logowania SSH:
  - **Użytkownik:** `root`
  - **Hasło:** `OpenCentauri`
- Adres IP drukarki w sieci lokalnej

## 🔧 Instalacja

### 1. Sklonuj lub pobierz repozytorium

```bash
git clone <url-repozytorium>
cd generator
```

### 2. Zainstaluj wymagane biblioteki

```bash
pip install -r requirements.txt
```

Lub ręcznie:

```bash
pip install paramiko scp deep-translator colorama
```

### 3. Uruchom skrypt

```bash
python translation_tool.py
```

## ⚙️ Konfiguracja

### Zapisywanie adresu IP drukarki

Przy pierwszym użyciu narzędzie poprosi o podanie adresu IP drukarki. Adres ten zostanie automatycznie zapisany w pliku `.printer_config.txt` w katalogu roboczym i będzie używany jako domyślna wartość przy kolejnych uruchomieniach.

Możesz również ręcznie edytować plik `.printer_config.txt` i wpisać tam adres IP drukarki.

### Sprawdzanie adresu IP drukarki

1. Sprawdź ustawienia sieciowe w menu drukarki
2. Lub użyj opcji **12. List Printer Files (Diagnostic)** w narzędziu, aby sprawdzić połączenie

## 📖 Użycie

### Podstawowy przepływ pracy

1. **Pobierz pliki z drukarki** (Opcja 1)
2. **Wygeneruj pliki tekstowe** (Opcja 2)
3. **Przetłumacz automatycznie** (Opcja 5) lub **edytuj ręcznie**
4. **Zastąp język** (Opcja 3) lub **dodaj nowy język** (Opcja 4)
5. **Wgraj pliki na drukarkę** (Opcja 8)
6. **Zrestartuj drukarkę** (Opcja 11) - opcjonalnie

### Przykład: Dodanie polskiego tłumaczenia

```bash
# 1. Uruchom narzędzie
python translation_tool.py

# 2. Wybierz opcję 1 - Pobierz pliki z drukarki
# 3. Wybierz opcję 2 - Wygeneruj pliki tekstowe
# 4. Wybierz opcję 5 - Automatyczne tłumaczenie
#    - Wpisz kod języka: pl
#    - Zatwierdź domyślną nazwę pliku: pl.txt
# 5. Sprawdź i popraw plik pl.txt (opcjonalnie)
# 6. Wybierz opcję 3 - Zastąp istniejący język
#    - Wybierz język do zastąpienia (np. English)
#    - Wpisz nazwę języka: Polski
#    - Wpisz nazwę pliku: pl.txt
# 7. Wybierz opcję 8 - Wgraj pliki na drukarkę
# 8. Wybierz opcję 11 - Zrestartuj drukarkę
```

## 📚 Szczegółowy opis opcji

### 1. Fetch files from Printer - UI Files (BIN/CSV)

**Funkcja:** Pobiera pliki `translation.csv` i `translation.bin` z drukarki przez SSH.

**Co robi:**
- Łączy się z drukarką przez SSH
- Pobiera pliki z katalogu `/app/resources/`
- Automatycznie wywołuje opcję 2 (wygenerowanie plików tekstowych)

**Wymagania:**
- Biblioteka `paramiko` zainstalowana
- Drukarka dostępna w sieci
- Poprawne dane logowania SSH

**Pliki wynikowe:**
- `translation.csv` - plik CSV z tłumaczeniami
- `translation.bin` - plik binarny z tłumaczeniami
- `chinese.txt` - wyekstrahowane teksty chińskie
- `english.txt` - wyekstrahowane teksty angielskie

---

### 2. Regenerate chinese.txt / english.txt from local CSV

**Funkcja:** Wyodrębnia teksty z lokalnego pliku `translation.csv` do plików tekstowych.

**Co robi:**
- Czyta lokalny plik `translation.csv`
- Wyodrębnia teksty chińskie do `chinese.txt`
- Wyodrębnia teksty angielskie do `english.txt`
- Automatycznie uzupełnia puste teksty angielskie (patches)

**Wymagania:**
- Plik `translation.csv` w katalogu roboczym

**Pliki wynikowe:**
- `chinese.txt` - jedna linia = jeden tekst
- `english.txt` - jedna linia = jeden tekst (z automatycznymi poprawkami i dodaniem brakujących tłumaczeń w oparciu o chiński)

---

### 3. Replace Existing Language (Recommended) - Overwrites column

**Funkcja:** Zastępuje istniejącą kolumnę języka nowymi tłumaczeniami. **Zalecana metoda** do aktualizacji tłumaczeń.

**Co robi:**
- Wyświetla listę dostępnych języków w pliku CSV
- Pozwala wybrać język do zastąpienia
- Wczytuje nowe tłumaczenia z pliku `.txt`
- Zastępuje wybraną kolumnę nowymi tłumaczeniami
- Generuje pliki `translation_updated.csv` i `translation_updated.bin`

**Kroki:**
1. Wybierz język do zastąpienia z listy
2. Wpisz nową nazwę języka (np. "Polski")
3. Wpisz nazwę pliku z tłumaczeniami (np. "pl.txt")
4. Narzędzie automatycznie dopasuje liczbę linii

**Wymagania:**
- Plik `translation.csv` w katalogu roboczym
- Plik z tłumaczeniami (np. `pl.txt`) w katalogu roboczym

**Pliki wynikowe:**
- `translation_updated.csv` - zaktualizowany plik CSV
- `translation_updated.bin` - zaktualizowany plik binarny

**Uwagi:**
- Jeśli plik z tłumaczeniami ma mniej linii, puste linie zostaną dodane automatycznie
- Jeśli plik ma więcej linii, nadmiarowe zostaną obcięte
- Oryginalna struktura CSV zostaje zachowana

---

### 4. Add New Language (Manual) - Appends column (limit 12)

**Funkcja:** Dodaje nową kolumnę języka do pliku CSV. **⚠️ EKSPERYMENTALNA - Firmware nie wyświetla nowych języków w menu!**

**Co robi:**
- Dodaje nową kolumnę języka przed ostatnią kolumną techniczną
- Wczytuje tłumaczenia z pliku `.txt`
- Generuje zaktualizowane pliki CSV i BIN

**Kroki:**
1. Wpisz nazwę nowego języka (np. "Polski")
2. Wpisz nazwę pliku z tłumaczeniami (np. "pl.txt")

**Wymagania:**
- Plik `translation.csv` w katalogu roboczym
- Plik z tłumaczeniami w katalogu roboczym
- Mniej niż 12 języków w pliku CSV

**Pliki wynikowe:**
- `translation_updated.csv` - z nową kolumną języka
- `translation_updated.bin` - zaktualizowany plik binarny

**Uwagi:**
- ⚠️ **EKSPERYMENTALNA:** Mimo dodania języka do pliku BIN, firmware nie wyświetla go w menu wyboru języka
- Nowy język jest dodawany przed ostatnią kolumną (kolumna techniczna)
- Jeśli limit języków został przekroczony, użyj opcji 3 (zastąpienie)
- **Zalecane:** Użyj opcji 3 (zastąpienie istniejącego języka) zamiast dodawania nowego

---

### 5. Generate Auto-Translation to target language (.txt)

**Funkcja:** Automatycznie tłumaczy plik `english.txt` na wybrany język przy użyciu Google Translate.

**Co robi:**
- Wczytuje plik `english.txt`
- Tłumaczy wszystkie linie na wybrany język
- Zapisuje wynik do pliku `.txt`
- Pokazuje postęp tłumaczenia w partiach

**Kroki:**
1. Wpisz kod języka docelowego (np. `pl` dla polskiego, `es` dla hiszpańskiego)
2. Wpisz nazwę pliku wyjściowego (domyślnie: `{kod}.txt`)

**Wymagania:**
- Biblioteka `deep-translator` zainstalowana
- Plik `english.txt` w katalogu roboczym
- Połączenie z internetem (do Google Translate)

**Pliki wynikowe:**
- `{kod}.txt` - przetłumaczony plik (np. `pl.txt`)

**Obsługiwane kody języków:**
- `pl` - Polski
- `es` - Hiszpański
- `fr` - Francuski
- `de` - Niemiecki
- `it` - Włoski
- `ru` - Rosyjski
- `ja` - Japoński
- `ko` - Koreański
- `tr` - Turecki
- `uk` - Ukraiński
- I wiele innych (zgodnie z Google Translate)

**Uwagi:**
- Tłumaczenie może zająć kilka minut (zależnie od liczby linii)
- Puste linie są zachowywane
- Tłumaczenie odbywa się w partiach po 50 linii
- Po automatycznym tłumaczeniu **zawsze sprawdź i popraw** tłumaczenia ręcznie!

---

### 6. Fetch files from Printer - Web Interface (JSON)

**Funkcja:** Pobiera plik tłumaczeń interfejsu webowego (`network-en.json`) z drukarki.

**Co robi:**
- Łączy się z drukarką przez SSH
- Pobiera plik `/app/resources/www/assets/i18n/network-en.json`
- Zapisuje do katalogu `web_i18n/`

**Wymagania:**
- Biblioteka `paramiko` zainstalowana
- Drukarka dostępna w sieci

**Pliki wynikowe:**
- `web_i18n/network-en.json` - plik JSON z tłumaczeniami interfejsu webowego

---

### 7. Translate Web Interface JSON

**Funkcja:** Automatycznie tłumaczy plik JSON interfejsu webowego na wybrany język.

**Co robi:**
- Wczytuje plik `web_i18n/network-en.json`
- Rekurencyjnie tłumaczy wszystkie wartości tekstowe
- Zapisuje przetłumaczony plik JSON

**Kroki:**
1. Wpisz kod języka docelowego (np. `pl`)

**Wymagania:**
- Biblioteka `deep-translator` zainstalowana
- Plik `web_i18n/network-en.json` (pobrany opcją 6)
- Połączenie z internetem

**Pliki wynikowe:**
- `web_i18n/network-en_patched_with_{kod}.json` - przetłumaczony plik JSON

**Uwagi:**
- Tłumaczenie może zająć dużo czasu (zależnie od liczby kluczy)
- Struktura JSON jest zachowywana (obsługuje zagnieżdżone obiekty i tablice)
- Po automatycznym tłumaczeniu **zawsze sprawdź i popraw** tłumaczenia ręcznie!

---

### 8. Upload to Printer - UI Files (translation.bin)

**Funkcja:** Wgrywa zaktualizowane pliki tłumaczeń UI na drukarkę.

**Co robi:**
- Tworzy kopie zapasowe oryginalnych plików na drukarkę
- Wgrywa pliki `translation_updated.bin` i `translation_updated.csv`
- Zastępuje oryginalne pliki na drukarce

**Wymagania:**
- Biblioteka `paramiko` zainstalowana
- Plik `translation_updated.bin` w katalogu roboczym
- Drukarka dostępna w sieci

**Kroki:**
1. Potwierdź wgranie plików (wpisz `yes`)

**Bezpieczeństwo:**
- Automatyczne tworzenie kopii zapasowych przed wgraniem
- Kopie zapasowe mają znacznik czasowy w nazwie
- Pliki są wgrywane przez tymczasowe nazwy (bezpieczne wgrywanie)

**Uwagi:**
- Po wgraniu może być konieczny restart drukarki (Opcja 11)
- Zmiany są widoczne po restarcie drukarki

---

### 9. Upload to Printer - Web Files (network-en.json)

**Funkcja:** Wgrywa przetłumaczony plik JSON interfejsu webowego na drukarkę.

**Co robi:**
- Tworzy kopię zapasową oryginalnego pliku JSON
- Wgrywa przetłumaczony plik JSON
- Zastępuje oryginalny plik na drukarce

**Wymagania:**
- Biblioteka `paramiko` zainstalowana
- Przetłumaczony plik JSON w katalogu `web_i18n/`
  - **Nazwa pliku:** `network-en_patched_with_{kod}.json` - **wymagana dla automatycznego i ręcznego tłumaczenia!**
  - Skrypt szuka plików pasujących do wzorca `network-en_patched_with_*.json`
- Drukarka dostępna w sieci

**Kroki:**
1. Jeśli jest wiele plików, wybierz plik do wgrania
2. Potwierdź wgranie plików (wpisz `yes`)

**Uwagi dotyczące nazwy pliku:**
- **Automatyczne tłumaczenie (Opcja 7):** Skrypt automatycznie tworzy plik o nazwie `network-en_patched_with_{kod}.json`
- **Ręczne tłumaczenie:** Plik **musi** mieć nazwę pasującą do wzorca `network-en_patched_with_*.json` (np. `network-en_patched_with_pl.json`, `network-en_patched_with_manual.json`)
- Skrypt wyszukuje tylko pliki pasujące do tego wzorca w katalogu `web_i18n/`

**Bezpieczeństwo:**
- Automatyczne tworzenie kopii zapasowej
- Kopia zapasowa ma znacznik czasowy w nazwie

**Uwagi:**
- Zmiany są widoczne po odświeżeniu strony w przeglądarce
- Nie jest wymagany restart drukarki

---

### 10. Patch Web Language Button (English → Your Language) 😎

**Funkcja:** Modyfikuje przycisk wyboru języka w interfejsie webowym, zmieniając tekst "English" na wybrany język, zachowując kod języka `en`.

**Co robi:**
- Pobiera plik JavaScript z drukarki
- Znajduje i zastępuje tekst "English" w przycisku języka
- Wgrywa zmodyfikowany plik z powrotem na drukarkę

**Kroki:**
1. Wpisz nazwę języka do wyświetlenia (np. "Polski", "Español")
2. Potwierdź modyfikację (wpisz `yes`)
3. Potwierdź wgranie pliku (wpisz `yes`)

**Wymagania:**
- Biblioteka `paramiko` zainstalowana
- Drukarka dostępna w sieci

**Pliki wynikowe:**
- `web_i18n/624.931d12e23af9a62e6007.js` - oryginalny plik
- `web_i18n/624.931d12e23af9a62e6007_patched.js` - zmodyfikowany plik

**Uwagi:**
- To jest "sneaky mod" - zmienia tylko wyświetlany tekst, kod języka pozostaje `en`
- Zmiany są widoczne po odświeżeniu strony w przeglądarce
- Automatyczne tworzenie kopii zapasowej przed modyfikacją
- Jeśli wzorzec nie zostanie znaleziony, narzędzie zapyta, czy kontynuować

---

### 11. Reboot Printer 🔄

**Funkcja:** Restartuje drukarkę przez SSH.

**Co robi:**
- Łączy się z drukarką przez SSH
- Wysyła komendę `reboot`
- Informuje o czasie oczekiwania

**Wymagania:**
- Biblioteka `paramiko` zainstalowana
- Drukarka dostępna w sieci

**Kroki:**
1. Potwierdź restart (wpisz `yes`)

**Uwagi:**
- ⚠️ **UWAGA:** To spowoduje natychmiastowy restart drukarki
- Po restarcie poczekaj 1-2 minuty przed ponownym połączeniem
- Jeśli drukarka drukuje, restart przerwie drukowanie!

---

### 12. List Printer Files (Diagnostic) 🔍

**Funkcja:** Wyświetla listę plików w katalogu `/app/resources` na drukarkę (narzędzie diagnostyczne).

**Co robi:**
- Łączy się z drukarką przez SSH
- Wyświetla listę plików w `/app/resources`
- Szuka plików konfiguracyjnych (`.json`, `.conf`, `config*`)

**Wymagania:**
- Biblioteka `paramiko` zainstalowana
- Drukarka dostępna w sieci

**Użycie:**
- Przydatne do diagnostyki problemów
- Pomaga sprawdzić, czy pliki zostały poprawnie wgrane
- Pozwala zobaczyć strukturę katalogów na drukarkę

---

### 13. Exit

**Funkcja:** Zamyka narzędzie.

---

## 📁 Struktura plików

### Pliki źródłowe
```
generator/
├── translation_tool.py      # Główny skrypt
├── requirements.txt         # Lista zależności
├── README.md               # Ta dokumentacja
└── .printer_config.txt     # Zapisany adres IP drukarki (tworzony automatycznie)
```

### Pliki generowane podczas pracy

#### Pliki UI (interfejs ekranu dotykowego)
```
generator/
├── translation.csv              # Oryginalny plik CSV z drukarki
├── translation.bin             # Oryginalny plik binarny z drukarki
├── translation_updated.csv      # Zaktualizowany plik CSV
├── translation_updated.bin      # Zaktualizowany plik binarny
├── chinese.txt                  # Wyekstrahowane teksty chińskie
├── english.txt                  # Wyekstrahowane teksty angielskie
├── pl.txt                       # Przykład: polskie tłumaczenia
└── {kod_języka}.txt            # Inne pliki tłumaczeń
```

#### Pliki Web (interfejs webowy)
```
generator/
└── web_i18n/
    ├── network-en.json                          # Oryginalny plik JSON
    ├── network-en_patched_with_{kod}.json      # Przetłumaczony plik JSON
    ├── 624.931d12e23af9a62e6007.js            # Oryginalny plik JavaScript
    └── 624.931d12e23af9a62e6007_patched.js     # Zmodyfikowany plik JavaScript
```

### Pliki kopii zapasowych na drukarkę

Kopie zapasowe są tworzone automatycznie na drukarce w następujących lokalizacjach:
- `/app/resources/translation.bin.backup_{timestamp}`
- `/app/resources/translation.csv.backup_{timestamp}`
- `/app/resources/www/assets/i18n/network-en.json.backup_{timestamp}`
- `/app/resources/www/624.931d12e23af9a62e6007.js.backup_{timestamp}`

## ⚠️ Znane błędy i ograniczenia

### Błąd: Nowe języki nie są wyświetlane w menu drukarki

**Problem:** Mimo dodania nowego języka do pliku BIN (opcja 3 - zastąpienie lub opcja 4 - dodanie), firmware drukarki nie wyświetla go w menu wyboru języka.

**Szczegóły:**
- Język jest poprawnie dodany do pliku `translation.bin`
- Plik został poprawnie wgrany na drukarkę
- Menu wyboru języka w interfejsie drukarki nie pokazuje nowego języka
- Jest to ograniczenie firmware, nie narzędzia

**Workaround:** Użyj opcji 3 (zastąpienie istniejącego języka) zamiast dodawania nowego. Zastąp język, którego nie używasz (np. hiszpański, francuski) swoim tłumaczeniem.

---

### Błąd: Nazwa języka w menu pozostaje niezmieniona po podmianie

**Problem:** Po zastąpieniu języka (opcja 3), w menu wyboru języka nadal wyświetla się oryginalna nazwa języka, który został podmieniony.

**Przykład:**
- Zastępujesz język "Italian" (włoski) tłumaczeniem polskim
- Wpisujesz nową nazwę: "Polski"
- Po wgraniu i restarcie, w menu wyboru języka nadal widzisz "Italian" zamiast "Polski"

**Szczegóły:**
- Tłumaczenia działają poprawnie (wyświetlają się po wybraniu języka)
- Problem dotyczy tylko nazwy języka w menu wyboru
- Jest to ograniczenie firmware, nie narzędzia

**Workaround:** Użyj opcji 10 (Patch Web Language Button) dla interfejsu webowego, aby zmienić wyświetlaną nazwę języka. Dla interfejsu ekranu dotykowego nie ma obecnie rozwiązania.

---

### Ograniczenie: Opcja 4 (Dodaj nowy język) jest eksperymentalna

**Problem:** Opcja 4 pozwala dodać nowy język do pliku BIN, ale firmware nie rozpoznaje go w menu wyboru języka.

**Szczegóły:**
- Język jest poprawnie dodany do struktury pliku BIN
- Firmware OpenCentauri ma hardcoded listę języków w menu
- Nowe języki nie są uwzględniane w tej liście

**Zalecenie:** Zawsze używaj opcji 3 (zastąpienie istniejącego języka) zamiast opcji 4.

## 🔧 Rozwiązywanie problemów

### Problem: "paramiko module not installed"

**Rozwiązanie:**
```bash
pip install paramiko
```

### Problem: "deep-translator module not installed"

**Rozwiązanie:**
```bash
pip install deep-translator
```

### Problem: "Connection failed"

**Możliwe przyczyny:**
1. Nieprawidłowy adres IP drukarki
2. Drukarka nie jest włączona lub nie jest dostępna w sieci
3. Firewall blokuje połączenie SSH
4. Nieprawidłowe dane logowania SSH

**Rozwiązanie:**
1. Sprawdź adres IP drukarki w ustawieniach sieciowych
2. Upewnij się, że drukarka jest włączona i połączona z tą samą siecią
3. Sprawdź ustawienia firewalla
4. Sprawdź, czy domyślne dane logowania są poprawne (root/OpenCentauri)

### Problem: "translation.csv not found"

**Rozwiązanie:**
1. Najpierw użyj opcji 1, aby pobrać pliki z drukarki
2. Upewnij się, że plik `translation.csv` znajduje się w katalogu roboczym

### Problem: "Translation failed"

**Możliwe przyczyny:**
1. Brak połączenia z internetem
2. Google Translate zablokował żądania (rate limiting)
3. Nieprawidłowy kod języka

**Rozwiązanie:**
1. Sprawdź połączenie z internetem
2. Poczekaj kilka minut i spróbuj ponownie
3. Sprawdź, czy kod języka jest poprawny (np. `pl`, `es`, `fr`)

### Problem: Plik z tłumaczeniami ma złą liczbę linii

**Rozwiązanie:**
- Narzędzie automatycznie dopasowuje liczbę linii:
  - Jeśli plik ma mniej linii, puste linie zostaną dodane
  - Jeśli plik ma więcej linii, nadmiarowe zostaną obcięte
- Upewnij się, że plik `english.txt` ma poprawną liczbę linii (użyj opcji 2)

### Problem: Kolory nie działają w terminalu

**Rozwiązanie:**
```bash
pip install colorama
```

Narzędzie będzie działać bez kolorów, ale z mniejszą czytelnością.

### Problem: Zmiany nie są widoczne po wgraniu

**Rozwiązanie:**
1. Zrestartuj drukarkę (Opcja 11)
2. Dla interfejsu webowego: odśwież stronę w przeglądarce (Ctrl+F5)
3. Sprawdź, czy pliki zostały poprawnie wgrane (Opcja 12)

## 🔬 Informacje techniczne

### Format pliku BIN

Plik `translation.bin` ma następującą strukturę:

```
[Header - 15 bajtów]
- Magic: 00 10 FD 12 (4 bajty)
- Total size - 14 (4 bajty, little-endian)
- Reserved: 00 00 (2 bajty)
- Version: 01 (1 bajt)
- Language count (1 bajt)
- String count (2 bajty, little-endian)
- Reserved: 00 (1 bajt)

[Offset List]
- 4 bajty na język (offset do tabeli języka)

[Language Tables]
- 8 bajtów na string (offset + długość)

[String Blob]
- UTF-8 stringi zakończone null byte
```

### Format pliku CSV

Plik `translation.csv` jest plikiem TSV (Tab-Separated Values):
- Kolumna 0: ID stringa
- Kolumna 1: Rozmiar czcionki (Aux)
- Kolumna 2+: Tłumaczenia dla każdego języka
- Ostatnia kolumna: Kolumna techniczna (结束列)

### Format pliku JSON (Web)

Plik `network-en.json` to standardowy plik JSON z tłumaczeniami interfejsu webowego. Może zawierać zagnieżdżone obiekty i tablice.

### Protokół SSH

Narzędzie używa protokołu SSH do komunikacji z drukarką:
- Port: 22 (domyślny)
- Użytkownik: `root`
- Hasło: `OpenCentauri`
- Protokół: SSH2

### API Google Translate

Narzędzie używa biblioteki `deep-translator`, która korzysta z Google Translate API:
- Limit: ~5000 znaków na żądanie
- Rate limiting: automatycznie obsługiwany przez bibliotekę
- Batch processing: tłumaczenie w partiach po 50 linii

## 🔒 Bezpieczeństwo

### ⚠️ Ostrzeżenia

1. **Dane logowania SSH:** Narzędzie używa domyślnych danych logowania drukarki. Jeśli zmieniłeś hasło, musisz zmodyfikować skrypt.

2. **Kopie zapasowe:** Narzędzie automatycznie tworzy kopie zapasowe przed modyfikacją plików na drukarkę. Jednak zawsze zalecane jest ręczne utworzenie kopii zapasowej przed rozpoczęciem pracy.

3. **Restart drukarki:** Opcja 11 natychmiast restartuje drukarkę. Upewnij się, że nie drukujesz w tym momencie!

4. **Modyfikacja plików:** Modyfikacja plików systemowych drukarki może spowodować problemy. Używaj narzędzia na własną odpowiedzialność.

### Zalecenia bezpieczeństwa

1. **Testuj na nieużywanej drukarce:** Jeśli to możliwe, testuj zmiany na drukarce, która nie jest używana do produkcji.

2. **Zachowaj kopie zapasowe:** Przed wgraniem zmian zawsze zachowaj kopie zapasowe oryginalnych plików.

3. **Sprawdź tłumaczenia:** Zawsze sprawdź automatyczne tłumaczenia przed wgraniem na drukarkę.

4. **Sieć lokalna:** Używaj narzędzia tylko w zaufanej sieci lokalnej.

## 👤 Autor

**Czajo**

Narzędzie stworzone do tłumaczenia interfejsu drukarek 3D ELEGOO Centauri Carbon.

## 📝 Licencja

Narzędzie jest udostępnione do użytku osobistego. Używaj na własną odpowiedzialność.

---

## 🎨 Kolory komunikatów

Narzędzie używa kolorowych komunikatów dla lepszej czytelności:

- 🔴 **Czerwony** - Błędy
- 🟢 **Zielony** - Sukcesy
- 🟡 **Żółty** - Ostrzeżenia
- 🔵 **Cyan** - Informacje
- 🔵 **Niebieski (pogrubiony)** - Nagłówki

---

## 📞 Wsparcie

W przypadku problemów:
1. Sprawdź sekcję [Rozwiązywanie problemów](#rozwiązywanie-problemów)
2. Sprawdź, czy wszystkie wymagane biblioteki są zainstalowane
3. Sprawdź połączenie z drukarką i internetem
4. Sprawdź logi błędów w terminalu

---

**Powodzenia w tłumaczeniu! 🚀**
