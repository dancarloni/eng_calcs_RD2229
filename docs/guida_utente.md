# Guida Utente - Verifiche DM 2229/1939

## Indice
1. [Installazione](#installazione)
2. [Primi Passi](#primi-passi)
3. [Configurazione](#configurazione)
4. [Utilizzo CLI](#utilizzo-cli)
5. [Utilizzo da Python](#utilizzo-da-python)
6. [Import/Export CSV](#importexport-csv)
7. [Grafici e Report](#grafici-e-report)
8. [Esempi Pratici](#esempi-pratici)

## Installazione

### Requisiti
- Python 3.9 o superiore
- pip

### Procedura

1. **Installa Python** (se non presente):
   - Windows: https://www.python.org/downloads/
   - Seleziona "Add Python to PATH" durante l'installazione

2. **Crea ambiente virtuale** (consigliato):
```bash
python -m venv venv

# Attiva ambiente (Windows):
.\venv\Scripts\activate

# Attiva ambiente (Linux/Mac):
source venv/bin/activate
```

3. **Installa dipendenze**:
```bash
pip install -r requirements.txt
```

4. **Installa il pacchetto**:
```bash
pip install -e .
```

## Primi Passi

### Esecuzione esempio base

```bash
# Esegui esempio trave
python examples/esempio_trave.py
```

Questo creerà una directory `examples/output/` con:
- Grafici della sezione
- Diagramma tensioni
- Dominio M-N
- Report HTML completo

### Test validazione

```bash
# Verifica che i calcoli siano corretti
python tests/test_validazione.py
```

## Configurazione

### File YAML

Il software utilizza file YAML per configurare le verifiche.

**Esempio minimo** (`config/trave_minima.yaml`):

```yaml
materiali:
  calcestruzzo:
    rck: 15.0
    calcola_auto: true
  acciaio:
    tipo: "FeB32k"
    calcola_auto: true

sezione:
  base: 300
  altezza: 500
  copriferro: 30

armatura:
  longitudinale:
    diametro_inferiore: 16
    numero_barre_inferiori: 4

sollecitazioni:
  momento_flettente: 80.0
  taglio: 50.0
```

### Parametri Dettagliati

#### Materiali

**Calcestruzzo**:
```yaml
materiali:
  calcestruzzo:
    rck: 15.0  # Resistenza caratteristica [MPa]
    tensione_ammissibile_compressione: 5.0  # [MPa] - opzionale se calcola_auto=true
    tensione_ammissibile_taglio: 0.81  # [MPa] - opzionale
    coefficiente_omogeneizzazione: 15  # n = Es/Ec
    calcola_auto: true  # Calcola automaticamente tensioni ammissibili
```

**Acciaio**:
```yaml
materiali:
  acciaio:
    tipo: "FeB32k"  # FeB24k, FeB32k, FeB38k, FeB44k
    # OPPURE specificare manualmente:
    tensione_snervamento: 320.0  # [MPa]
    tensione_ammissibile: 140.0  # [MPa]
    calcola_auto: true
```

#### Sezione e Armatura

```yaml
sezione:
  tipo: "rettangolare"
  base: 300  # [mm]
  altezza: 500  # [mm]
  copriferro: 30  # [mm]

armatura:
  longitudinale:
    diametro_inferiore: 16  # [mm] - Armatura tesa
    numero_barre_inferiori: 4
    diametro_superiore: 12  # [mm] - Armatura compressa
    numero_barre_superiori: 2
  
  trasversale:
    diametro: 8  # [mm] - Staffe
    passo: 200  # [mm]
    bracci: 2  # Numero bracci
  
  ferri_piegati:
    usa: true
    diametro: 12  # [mm]
    numero: 2
    inclinazione: 45  # [gradi]
```

#### Sollecitazioni

```yaml
sollecitazioni:
  momento_flettente: 80.0  # [kNm]
  sforzo_normale: 0.0  # [kN] - positivo = compressione
  taglio: 50.0  # [kN]
  
  # Per pressoflessione deviata:
  momento_x: 100.0  # [kNm]
  momento_y: 50.0  # [kNm]
```

## Utilizzo CLI

### Verifica Trave

```bash
verifiche-dm1939 trave --config config/trave_esempio.yaml --output output/
```

### Verifica Pilastro

```bash
verifiche-dm1939 pilastro --config config/pilastro_esempio.yaml --output output/
```

### Generazione Template CSV

```bash
verifiche-dm1939 template --tipo trave --output template_trave.csv
verifiche-dm1939 template --tipo pilastro --output template_pilastro.csv
```

### Verifica Batch da CSV

```bash
verifiche-dm1939 batch --csv data/travi_esempio.csv --output output/
```

## Utilizzo da Python

### Esempio Completo

```python
from verifiche_dm1939.materials import Calcestruzzo, Acciaio
from verifiche_dm1939.sections import SezioneRettangolare
from verifiche_dm1939.verifications.verifica_flessione import VerificaFlessione

# 1. Definisci materiali
cls = Calcestruzzo(resistenza_caratteristica=15.0)
acciaio = Acciaio.da_tipo("FeB32k")

# 2. Crea sezione
sezione = SezioneRettangolare(base=300, altezza=500, copriferro=30)
sezione.aggiungi_armatura_inferiore(diametro=16, numero_barre=4)
sezione.aggiungi_staffe(diametro=8, passo=200)

# 3. Esegui verifica
verifica = VerificaFlessione(
    sezione=sezione,
    calcestruzzo=cls,
    acciaio=acciaio,
    momento_flettente=80.0
)

risultato = verifica.verifica()

# 4. Visualizza risultati
print(risultato.genera_report_breve())
print(f"Verificato: {risultato.verificato}")
print(f"Momento resistente: {risultato.momento_resistente:.2f} kNm")
```

### Verifica a Taglio

```python
from verifiche_dm1939.verifications.verifica_taglio import VerificaTaglio

verifica_taglio = VerificaTaglio(
    sezione=sezione,
    calcestruzzo=cls,
    acciaio=acciaio,
    taglio=50.0,
    metodo="santarella"
)

risultato = verifica_taglio.verifica()
```

### Pressoflessione Retta

```python
from verifiche_dm1939.verifications.verifica_pressoflessione import VerificaPressoflessioneRetta

verifica_pf = VerificaPressoflessioneRetta(
    sezione=sezione,
    calcestruzzo=cls,
    acciaio=acciaio,
    sforzo_normale=200.0,  # kN
    momento_flettente=100.0,  # kNm
    lunghezza_libera_inflessione=3000,  # mm
)

risultato = verifica_pf.verifica()
```

## Import/Export CSV

### Formato CSV

Il file CSV deve avere intestazioni che il sistema riconosce automaticamente:

```csv
base,altezza,copriferro,rck,tipo_acciaio,momento,taglio,diametro_inf,numero_inf
300,500,30,15,FeB32k,80,50,16,4
350,600,30,20,FeB38k,120,70,20,5
```

### Import da CSV

```python
from verifiche_dm1939.io_handlers.csv_handler import CSVHandler

# Importa dati
sezioni = CSVHandler.importa_sezioni("data/travi_esempio.csv")

# Crea sezione da dati
for dati in sezioni:
    sezione = CSVHandler.crea_sezione_da_dati(dati)
    # ... esegui verifiche
```

### Export Risultati

```python
risultati = [
    {
        "sezione": "Trave 1",
        "verificato": True,
        "momento_resistente": 85.5,
        # ... altri dati
    },
]

CSVHandler.esporta_risultati(risultati, "output/risultati.csv")
```

## Grafici e Report

### Generazione Grafici

```python
from verifiche_dm1939.reporting.grafici import GeneratoreGrafici

gen = GeneratoreGrafici()

# Disegna sezione
fig = gen.disegna_sezione(
    sezione=sezione,
    asse_neutro=140.0,
    titolo="Sezione Trave"
)
gen.salva_grafico(fig, "output/sezione.png")

# Diagramma tensioni
fig = gen.diagramma_tensioni_flessione(
    sezione=sezione,
    sigma_c=4.5,
    sigma_s=130.0,
    x=140.0,
    sigma_c_amm=5.0,
    sigma_s_amm=140.0
)
gen.salva_grafico(fig, "output/tensioni.png")

# Dominio M-N
fig = gen.dominio_momento_sforzo_normale(
    base=300,
    altezza=500,
    area_armatura_inf=800,
    area_armatura_sup=400,
    sigma_c_amm=5.0,
    sigma_s_amm=140.0
)
gen.salva_grafico(fig, "output/dominio.png")
```

### Generazione Report HTML

```python
from verifiche_dm1939.reporting.report_generator import GeneratoreReport

gen_report = GeneratoreReport()

risultati = [
    {
        "tipo": "flessione",
        "risultato": risultato_flessione,
        "sezione": sezione,
        "materiali": {
            "calcestruzzo": cls.to_dict(),
            "acciaio": acciaio.to_dict(),
        },
        "sollecitazioni": {"momento": 80.0},
    },
]

gen_report.genera_report_completo(
    risultati=risultati,
    filepath="output/relazione.html",
    titolo="Relazione di Calcolo",
    progettista="Ing. Rossi"
)
```

## Esempi Pratici

### 1. Verifica Trave Semplice

Vedi: `examples/esempio_trave.py`

### 2. Verifica con Configurazione YAML

Vedi: `config/trave_esempio.yaml`

### 3. Import Batch da CSV

Vedi: `data/travi_esempio.csv`

### 4. Validazione con Esempi Letteratura

Vedi: `tests/test_validazione.py`

## Risoluzione Problemi

### Python non trovato
Assicurati che Python sia nel PATH di sistema.

### ModuleNotFoundError
Installa le dipendenze: `pip install -r requirements.txt`

### Errori nei calcoli
Verifica che i parametri siano nelle unità corrette (mm, MPa, kN, kNm)

## Supporto

Per domande o segnalazioni: aprire una issue nel repository.
