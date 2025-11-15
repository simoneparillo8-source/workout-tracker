# Workout Tracker PRO (no login)

Versione PRO del Workout Tracker senza sistema di autenticazione.
Funzionalità principali:
- Gestione di due utenti di esempio: simone, antonio
- Aggiunta/Modifica/Rimozione esercizi
- Slider rapidi per aggiornare i pesi
- Registrazione delle sessioni nello storico (JSON)
- Grafico di progressione per ogni esercizio
- Esportazione CSV

## Come usare
1. Estrarre la cartella
2. Creare un ambiente virtuale (opzionale) e installare requisiti:
   ```
   pip install -r requirements.txt
   ```
3. Avviare:
   ```
   streamlit run app.py
   ```

## Deploy su Streamlit Cloud
- Carica la cartella su GitHub
- Vai su https://share.streamlit.io e deploya il repo (file principale app.py)