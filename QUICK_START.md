# 🚀 Quick Start - Verifiche DM 2229/1939

## Avvio Rapido in 3 Passi

### 1️⃣ Installa Python e Dipendenze

**Windows:**
```powershell
# Verifica Python installato (richiesto 3.9+)
python --version

# Se non installato, scarica da: https://www.python.org/downloads/
# Durante installazione seleziona "Add Python to PATH"

# Installa dipendenze
cd "c:\Users\DanieleCarloni\Tensioni ammissibili"
pip install -r requirements.txt
```

### 2️⃣ Esegui Primo Esempio

```powershell
# Esempio trave completo con grafici e report
python examples\esempio_trave.py
```

**Output generato in** `examples\output\`:
- ✅ `sezione_trave.png` - Disegno della sezione
- ✅ `tensioni_flessione.png` - Diagramma tensioni  
- ✅ `dominio_MN.png` - Dominio resistenza
- ✅ `relazione_calcolo.html` - Report completo (apri nel browser)

### 3️⃣ Test Validazione

```powershell
# Verifica correttezza calcoli con esempi Santarella
python tests\test_validazione.py
```

Dovresti vedere: **TEST SUPERATO ✓**

---

## 📋 Esempi di Utilizzo

### Esempio 1: Script Python Personalizzato

Crea `mia_verifica.py`:

```python
from verifiche_dm1939.materials import Calcestruzzo, Acciaio
from verifiche_dm1939.sections import SezioneRettangolare
from verifiche_dm1939.verifications.verifica_flessione import VerificaFlessione

# Materiali
cls = Calcestruzzo(resistenza_caratteristica=15.0)
acc = Acciaio.da_tipo("FeB32k")

# Sezione 300x500 con 4φ16
sezione = SezioneRettangolare(base=300, altezza=500, copriferro=30)
sezione.aggiungi_armatura_inferiore(diametro=16, numero_barre=4)

# Verifica M = 80 kNm
verifica = VerificaFlessione(sezione, cls, acc, momento_flettente=80.0)
risultato = verifica.verifica()

# Risultati
print(risultato.genera_report_breve())
```

Esegui: `python mia_verifica.py`

### Esempio 2: Configurazione YAML

Modifica `config\trave_esempio.yaml`:

```yaml
materiali:
  calcestruzzo:
    rck: 20.0  # Cambia resistenza
  acciaio:
    tipo: "FeB38k"  # Cambia tipo acciaio

sezione:
  base: 350
  altezza: 600

armatura:
  longitudinale:
    diametro_inferiore: 20
    numero_barre_inferiori: 5

sollecitazioni:
  momento_flettente: 120.0
  taglio: 70.0
```

Esegui verifica:
```powershell
python -m verifiche_dm1939.cli trave --config config\trave_esempio.yaml --output output\
```

### Esempio 3: Import Batch da CSV

Crea `mie_travi.csv`:

```csv
base,altezza,rck,tipo_acciaio,momento,taglio,diametro_inf,numero_inf
300,500,15,FeB32k,80,50,16,4
350,600,20,FeB38k,120,70,20,5
400,700,25,FeB44k,180,90,22,6
```

Script Python:

```python
from verifiche_dm1939.io_handlers.csv_handler import CSVHandler
from verifiche_dm1939.materials import Calcestruzzo, Acciaio
from verifiche_dm1939.verifications.verifica_flessione import VerificaFlessione

# Importa dati
sezioni_dati = CSVHandler.importa_sezioni("mie_travi.csv")

risultati = []
for dati in sezioni_dati:
    # Crea sezione
    sezione = CSVHandler.crea_sezione_da_dati(dati)
    
    # Materiali
    cls = Calcestruzzo(resistenza_caratteristica=dati["rck"])
    acc = Acciaio.da_tipo(dati["tipo_acciaio"])
    
    # Verifica
    verifica = VerificaFlessione(sezione, cls, acc, dati["momento"])
    ris = verifica.verifica()
    
    risultati.append({
        "sezione": f"{dati['base']}x{dati['altezza']}",
        "verificato": ris.verificato,
        "Mr": ris.momento_resistente,
    })

# Export
CSVHandler.esporta_risultati(risultati, "risultati_batch.csv")
print(f"Elaborate {len(risultati)} sezioni!")
```

---

## 🎨 Generazione Grafici

```python
from verifiche_dm1939.reporting.grafici import GeneratoreGrafici
from pathlib import Path

gen = GeneratoreGrafici()

# Disegna sezione
fig = gen.disegna_sezione(
    sezione=sezione,
    asse_neutro=140.0,
    titolo="La Mia Trave"
)

# Salva
output = Path("output")
output.mkdir(exist_ok=True)
gen.salva_grafico(fig, output / "mia_sezione.png")
```

---

## 📊 Report HTML

```python
from verifiche_dm1939.reporting.report_generator import GeneratoreReport

gen_report = GeneratoreReport()

risultati_per_report = [
    {
        "tipo": "flessione",
        "risultato": risultato_flessione,
        "sezione": sezione,
        "materiali": {
            "calcestruzzo": cls.to_dict(),
            "acciaio": acc.to_dict(),
        },
        "sollecitazioni": {"momento": 80.0},
    }
]

gen_report.genera_report_completo(
    risultati=risultati_per_report,
    filepath="mio_report.html",
    titolo="Mia Relazione di Calcolo",
    progettista="Ing. Mario Rossi"
)
```

Apri `mio_report.html` nel browser!

---

## 🛠️ Troubleshooting

### ❌ "Python non trovato"
```powershell
# Installa Python da https://www.python.org/downloads/
# Seleziona "Add Python to PATH" durante installazione
```

### ❌ "ModuleNotFoundError: No module named 'numpy'"
```powershell
pip install -r requirements.txt
```

### ❌ "No module named 'verifiche_dm1939'"
```powershell
# Assicurati di essere nella directory corretta
cd "c:\Users\DanieleCarloni\Tensioni ammissibili"

# Installa in modalità sviluppo
pip install -e .
```

### ❌ Grafici non si visualizzano
```python
# Aggiungi alla fine dello script
import matplotlib.pyplot as plt
plt.show()  # Mostra i grafici
```

---

## 📚 Documentazione Completa

- **Guida Utente**: `docs\guida_utente.md`
- **Dettagli Implementazione**: `docs\COMPLETAMENTO.md`
- **Esempi**: `examples\`
- **Configurazioni**: `config\`
- **README**: `README.md`

---

## ✅ Checklist Prima Verifica

- [ ] Python 3.9+ installato
- [ ] Dipendenze installate (`pip install -r requirements.txt`)
- [ ] Esempio base eseguito (`python examples\esempio_trave.py`)
- [ ] Output generato in `examples\output\`
- [ ] Report HTML aperto nel browser
- [ ] Test validazione superato

---

## 🎯 Prossimi Passi

1. Studia l'esempio `examples\esempio_trave.py`
2. Modifica `config\trave_esempio.yaml` con i tuoi dati
3. Crea le tue verifiche personalizzate
4. Genera report per i tuoi progetti

**Buon lavoro con le verifiche DM 2229/1939!** 🏗️
