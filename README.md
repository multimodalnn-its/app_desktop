# ITS — Project Manager

Applicazione desktop per la gestione progetti del team ITS.

---

## Requisiti

- **Python 3.8+** (scaricabile da https://www.python.org/downloads/)
- Nessuna dipendenza esterna: usa solo la libreria standard di Python (tkinter incluso)

> Su **Windows** Python include già tkinter.  
> Su **macOS**: `brew install python-tk` se tkinter manca.  
> Su **Linux (Ubuntu/Debian)**: `sudo apt install python3-tk`

---

## Avvio

```bash
# Nella cartella dell'app:
python app.py
```

Oppure su Windows doppio clic su `avvia.bat`.

---

## Primo avvio

Al primo avvio ti verrà chiesto di impostare una **password personale**.  
La password viene salvata in forma cifrata (SHA-256) nel file `data/config.json`.

---

## Funzionalità

| Funzione | Descrizione |
|---|---|
| 🔒 Login | Accesso protetto da password |
| 📋 Lista progetti | Vista di tutti i progetti con filtri per stato |
| ➕ Nuovo progetto | Crea progetto con titolo, cliente, scadenza, stato, note |
| ✏️ Modifica | Modifica qualsiasi progetto esistente |
| 🗑️ Elimina | Rimuovi progetti con conferma |
| 📊 Statistiche | Conteggi per stato e scadenze imminenti (14 gg) |
| 🔑 Cambia password | Accessibile dalla sidebar in basso |

---

## Struttura file

```
its_pm_app/
├── app.py          ← applicazione principale
├── avvia.bat       ← avvio rapido Windows
├── README.md       ← questo file
├── assets/
│   └── logo.svg    ← logo ITS
└── data/           ← creata automaticamente
    ├── config.json ← configurazione (password cifrata)
    └── projects.json ← dati progetti
```

---

## Sicurezza

- La password non è mai salvata in chiaro
- I dati rimangono **solo sul tuo PC**, nessuna connessione a internet
- Per resettare la password: elimina `data/config.json` e riavvia l'app

---

*ITS — Image To Sound · Project Manager v1.0*
