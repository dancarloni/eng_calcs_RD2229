# Verifiche Strutturali DM 2229/1939

Software professionale per verifiche alle tensioni ammissibili di strutture in calcestruzzo armato secondo il **Regio Decreto Legge n. 2229 del 16 novembre 1939** - Norme tecniche per le costruzioni.

## 📋 Descrizione

Questo software implementa le metodologie di calcolo e verifica strutturale secondo:
- **Normativa**: DM 2229/1939 - Norme per l'esecuzione delle opere in conglomerato cementizio
- **Teorie di riferimento**: Santarella e Giangreco
- **Metodo**: Progetto simulato con verifica alle tensioni ammissibili

## 🎯 Funzionalità

### Verifiche Implementate
- ✅ **Travi in calcestruzzo armato**
  - Flessione semplice
  - Taglio con staffe e ferri piegati
  - Verifica a punzonamento

- ✅ **Pilastri**
  - Pressoflessione retta
  - Pressoflessione deviata
  - Carico di punta

- ✅ **Verifiche a taglio**
  - Contributo del calcestruzzo
  - Contributo delle staffe
  - Contributo dei ferri piegati
  - Verifica combinata

### Caratteristiche Principali
- 🔧 **Altamente configurabile**: ogni parametro personalizzabile
- 🎛️ **Modalità duale**: calcoli automatici o input manuali tramite flag
- 📊 **Import/Export**: caricamento bulk da CSV con intestazioni
- 📈 **Grafici dettagliati**: diagrammi di sollecitazione, tensioni, domini di rottura
- 📄 **Report completi**: generazione automatica di relazioni di calcolo
- ✔️ **Validazione**: confronto con esempi della letteratura tecnica

## 🏗️ Architettura

```
verifiche-dm1939/
├── src/verifiche_dm1939/
│   ├── core/              # Classi base e utilities
│   ├── materials/         # Database materiali e proprietà
│   ├── sections/          # Geometria sezioni e armature
│   ├── verifications/     # Motori di calcolo e verifica
│   ├── io_handlers/       # Import/Export CSV, Excel
│   ├── reporting/         # Generazione report e grafici
│   └── cli.py            # Interfaccia a riga di comando
├── config/               # File di configurazione
├── data/                 # Database materiali e esempi
├── examples/             # Esempi di utilizzo
├── tests/                # Test di validazione
└── docs/                 # Documentazione tecnica
```

## 📦 Installazione

### Requisiti
- Python >= 3.9
- pip

### Installazione standard
```bash
# Clona il repository
git clone <repository-url>
cd "Tensioni ammissibili"

# Crea ambiente virtuale
python -m venv venv

# Attiva ambiente virtuale
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Installa dipendenze
pip install -r requirements.txt

# Installa il pacchetto
pip install -e .
```

### Installazione per sviluppo
```bash
pip install -e ".[dev]"
```

## 🚀 Utilizzo

### Interfaccia a riga di comando

```bash
# Verifica trave
verifiche-dm1939 trave --input data/trave_esempio.csv --output report_trave.pdf

# Verifica pilastro pressoflessione retta
verifiche-dm1939 pilastro --tipo retta --input data/pilastro.csv

# Verifica pressoflessione deviata
verifiche-dm1939 pilastro --tipo deviata --config config/pilastro_config.yaml

# Verifica a taglio
verifiche-dm1939 taglio --staffe --ferri-piegati --input data/taglio.csv
```

### Utilizzo da Python

```python
from verifiche_dm1939.materials import Calcestruzzo, Acciaio
from verifiche_dm1939.sections import SezioneRettangolare
from verifiche_dm1939.verifications import VerificaTrave

# Definisci materiali
cls = Calcestruzzo(resistenza_caratteristica=15.0)  # Rck 15 MPa
acciaio = Acciaio(tipo="FeB32k", tensione_ammissibile=140.0)  # MPa

# Definisci sezione
sezione = SezioneRettangolare(
    base=300,  # mm
    altezza=500,  # mm
    copriferro=30  # mm
)

# Aggiungi armatura
sezione.aggiungi_armatura(
    diametro=16,  # mm
    numero_barre=4,
    posizione="inferiore"
)

# Esegui verifica
verifica = VerificaTrave(
    sezione=sezione,
    calcestruzzo=cls,
    acciaio=acciaio,
    momento_flettente=80.0,  # kNm
    taglio=50.0  # kN
)

risultati = verifica.esegui()
print(risultati.genera_report())
```

### Import da CSV

Il formato CSV deve includere le intestazioni:

```csv
tipo,base,altezza,copriferro,rck,acciaio,momento,taglio,staffe_diam,staffe_passo
trave,300,500,30,15,FeB32k,80,50,8,200
pilastro,400,400,30,20,FeB38k,100,200,10,150
```

## 📊 Configurazione

File di configurazione YAML di esempio:

```yaml
# config/verifica_config.yaml
materiali:
  calcestruzzo:
    rck: 15.0  # MPa
    tensione_ammissibile_compressione: 5.0  # MPa
    tensione_ammissibile_taglio: 0.8  # MPa
    coefficiente_omogeneizzazione: 15
    calcola_auto: true  # Se false, usa valori manuali
  
  acciaio:
    tipo: "FeB32k"
    tensione_ammissibile: 140.0  # MPa
    modulo_elastico: 206000.0  # MPa
    calcola_auto: true

sezione:
  tipo: "rettangolare"
  base: 300  # mm
  altezza: 500  # mm
  copriferro: 30  # mm

armatura:
  longitudinale:
    diametro: 16  # mm
    numero_barre_inferiori: 4
    numero_barre_superiori: 2
  trasversale:
    tipo: "staffe"
    diametro: 8  # mm
    passo: 200  # mm
    bracci: 2
  ferri_piegati:
    usa: true
    diametro: 12  # mm
    numero: 2
    inclinazione: 45  # gradi

sollecitazioni:
  momento_flettente: 80.0  # kNm
  sforzo_normale: 0.0  # kN (positivo = compressione)
  taglio: 50.0  # kN

opzioni_calcolo:
  metodo: "santarella"  # o "giangreco"
  genera_grafici: true
  formato_output: "pdf"  # o "html", "docx"
```

## 🧪 Test e Validazione

Il software include test di validazione con esempi dalla letteratura:

```bash
# Esegui tutti i test
pytest

# Test con coverage
pytest --cov

# Test specifico esempio Santarella
pytest tests/test_esempi_santarella.py -v
```

## 📚 Riferimenti Normativi e Tecnici

### Normativa
- **R.D.L. 2229/1939**: Norme per l'esecuzione delle opere in conglomerato cementizio semplice od armato
- **R.D. 16 novembre 1939 n. 2228**: Norme per l'accettazione dei materiali

### Testi di riferimento
- **Santarella, L.** - "Il cemento armato" - Hoepli
- **Giangreco, E.** - "Teoria e tecnica delle costruzioni"
- **Mezzina, M.** - "Verifica delle strutture in cemento armato"

## 🤝 Contributi

Contributi, segnalazioni di bug e richieste di funzionalità sono benvenuti!

## 📄 Licenza

Questo progetto è distribuito sotto licenza MIT.

## ⚠️ Note Legali

Questo software è fornito a scopo didattico e di ricerca. Le verifiche strutturali devono sempre essere eseguite e validate da professionisti abilitati secondo le normative vigenti.

## 📞 Contatti

Per domande o supporto, aprire una issue nel repository.

---

**Versione**: 0.1.0  
**Ultimo aggiornamento**: Gennaio 2026
