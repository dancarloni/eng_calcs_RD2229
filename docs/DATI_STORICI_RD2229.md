# Dati Storici RD 2229/1939 - Implementazione

## Fonte

**Regio Decreto Legge n. 2229 del 16 novembre 1939**
- Norme tecniche per l'esecuzione delle opere in conglomerato cementizio
- Prontuari dell'Ing. Luigi Santarella (anni '30-'70)
- Scansioni storiche analizzate e implementate

## Tabelle Implementate

### 1. **Tabella II - Rapporti Acqua/Cemento e Resistenze**

Resistenze di compressione a 28 giorni [Kg/cm²]:

| A/C  | Cemento Normale | Alta Resistenza | Alluminoso |
|------|-----------------|-----------------|-----------|
| 0,40 | 380             | 500             | 400       |
| 0,45 | 330             | 400             | 330       |
| 0,50 | 280             | 350             | 280       |
| 0,55 | 250             | 290             | -         |
| 0,60 | 225             | 250             | -         |
| 0,70 | 180             | 200             | -         |
| 0,80 | 140             | 170             | -         |

**Fonte**: Pagina 9 del documento RD 2229

---

### 2. **Carichi Unitari di Sicurezza**

#### Compressione nel Calcestruzzo [Kg/cm²]

- **Sezioni semplicemente compresse** (pilastri):
  - Cemento normale: σc = 35 Kg/cm² (con σcss > 120 Kg/cm²)
  - Cemento alta resistenza: σc = 45 Kg/cm²

- **Sezioni inflesse e presso-inflesse**:
  - Cemento normale: σc = 40 Kg/cm² (con σcss > 120 Kg/cm²)
  - Cemento alta resistenza: σc = 50 Kg/cm² (con σcss > 160 Kg/cm²)

#### Taglio nel Calcestruzzo [Kg/cm²]

- Cemento normale: τ = 4 Kg/cm²
- Cemento alta resistenza: τ = 6 Kg/cm²
- Cemento alluminoso: τ = 6 Kg/cm²

#### Acciai da Armatura [Kg/cm²]

**Acciaio Dolce** (FeB24k, FeB32k):
- Tensione massima: σf,max = 1400 Kg/cm²

**Acciaio Semiriduro** (FeB38k):
- Tensione massima: σf,max = 1800 Kg/cm²

**Acciaio Duro** (FeB44k):
- Barre φ < 26 mm: σf,max = 1600 Kg/cm²
- Barre φ ≥ 26 mm: σf,max = 2000 Kg/cm²

**Fonte**: Pagine 14-15 del documento RD 2229

---

### 3. **Moduli di Elasticità - Formule Storiche**

#### Formula di Santarella per Calcestruzzo

$$E_c = \frac{550000 \cdot \sigma_c}{\sigma_c + 200} \text{ [Kg/cm²]}$$

Dove σc = resistenza a compressione in Kg/cm²

**Esempio**: Per σc = 280 Kg/cm²
- Ec = 550000 × 280 / (280 + 200) = 320.833 Kg/cm² ≈ 31.500 MPa
- n = Es/Ec = 2.000.000 / 320.833 ≈ 6,2

#### Modulo Elastico Acciaio

- Es = 2.000.000 Kg/cm² ≈ 196.000 MPa (fisso per tutta l'epoca)

#### Coefficiente di Omogeneizzazione

$$n = \frac{E_s}{E_c}$$

Tipicamente:
- Per σc = 250-280 Kg/cm²: n ≈ 6,2-6,5
- Per σc = 350 Kg/cm²: n ≈ 5,7

**Fonte**: Pagine 13-14 del documento RD 2229

---

## Implementazione nel Codice

### Modulo: `dati_storici_rd2229.py`

```python
from verifiche_dm1939.core.dati_storici_rd2229 import (
    TABELLA_II_CALCESTRUZZO,
    CarichUnitariSicurezza,
    modulo_elasticita_calcestruzzo_kgcm2,
    interpola_resistenza_calcestruzzo,
)
```

**Contenuto**:
- Dizionario `TABELLA_II_CALCESTRUZZO` con tutti i dati tabulati
- Classe `CarichUnitariSicurezza` con costanti
- Funzione `modulo_elasticita_calcestruzzo_kgcm2()` per formula storica
- Funzione `interpola_resistenza_calcestruzzo()` per A/C intermedi

### Modulo: `conversioni_unita.py`

```python
from verifiche_dm1939.core.conversioni_unita import (
    kgcm2_to_mpa,
    mpa_to_kgcm2,
)
```

**Conversione**:
- 1 MPa = 10.197 Kg/cm² ≈ 10,2 Kg/cm²
- 1 Kg/cm² = 0.09807 MPa ≈ 0,098 MPa

### Factory Methods

#### Calcestruzzo da Tabella Storica

```python
from verifiche_dm1939.materials.calcestruzzo import Calcestruzzo

# Crea calcestruzzo con A/C=0.50, cemento normale → σc=280 Kg/cm²
cls = Calcestruzzo.da_tabella_storica(
    resistenza_compressione_kgcm2=280,
    tipo_cemento="normale",
    rapporto_ac=0.50
)

print(f"Ec = {cls.modulo_elastico:.0f} MPa")
print(f"σc,amm = {cls.tensione_ammissibile_compressione:.2f} MPa")
print(f"n = {cls.coefficiente_omogeneizzazione:.1f}")
```

#### Acciaio da Tabella Storica

```python
from verifiche_dm1939.materials.acciaio import Acciaio

# Crea acciaio dolce da tabella storica
acc = Acciaio.da_tabella_storica(
    resistenza_kgcm2=1400,
    tipo_acciaio="dolce"
)

print(f"fyk = {acc.tensione_snervamento:.0f} MPa")
print(f"σs,amm = {acc.tensione_ammissibile:.1f} MPa")
```

---

## Confronto: Metodo Storico vs Moderno

Per Rck = 27.5 MPa (280 Kg/cm²):

| Parametro | Metodo Moderno | Metodo Storico | Diff. |
|-----------|---------------|----------------|-------|
| σc,amm    | 9,17 MPa (Rck/3) | 3,92 MPa (carico unitario) | -57% |
| τc,amm    | 1,49 MPa (0.054·Rck) | 0,39 MPa (tab. 4 Kg/cm²) | -74% |
| Ec        | 29.891 MPa (5700·√Rck) | 31.483 MPa (formula storica) | +5% |
| n         | 6,7 | 6,2 | -7% |

**Nota**: Il metodo storico è più conservativo nelle tensioni ammissibili.

---

## Validazione

### Test Santarella - Trave C.A.

Scenario storico RD 2229:
- **Sezione**: 300×500 mm
- **Cls**: σc = 280 Kg/cm² (A/C=0.50, cemento normale)
- **Acciaio**: 1400 Kg/cm² (acciaio dolce FeB32k)
- **Armatura**: 4φ16
- **Momento**: 80 kNm

**Risultati attesi** (da letteratura Santarella):
- Asse neutro: x ≈ 140-150 mm
- Momento resistente: Mr ≈ 85-90 kNm

---

## Utilizzo nei Calcoli di Verifica

### Verifica a Flessione

```python
from verifiche_dm1939.verifications.verifica_flessione import VerificaFlessione

# Materiali da tabella storica
cls_storico = Calcestruzzo.da_tabella_storica(280, "normale", 0.50)
acc_storico = Acciaio.da_tabella_storica(1400, "dolce")

# Verifica
verifica = VerificaFlessione(sezione, cls_storico, acc_storico, 80)
risultato = verifica.verifica()

print(f"Momento resistente: {risultato.momento_resistente:.2f} kNm")
print(f"σc = {risultato.tensione_calcestruzzo:.2f} MPa")
print(f"σs = {risultato.tensione_acciaio:.2f} MPa")
```

---

## File Modificati/Creati

1. **`src/verifiche_dm1939/core/dati_storici_rd2229.py`** (NEW)
   - Tabelle RD 2229 complete
   - Formule storiche
   - Funzioni di interpolazione

2. **`src/verifiche_dm1939/core/conversioni_unita.py`** (NEW)
   - Conversioni Kg/cm² ↔ MPa

3. **`src/verifiche_dm1939/materials/calcestruzzo.py`** (MODIFIED)
   - Parametro `da_tabella_storica`
   - Metodo `da_tabella_storica()`
   - Funzione `_calcola_parametri_storici()`

4. **`src/verifiche_dm1939/materials/acciaio.py`** (MODIFIED)
   - Metodo `da_tabella_storica()`
   - Import da dati storici

5. **`tests/test_validazione.py`** (UPDATED)
   - Test con dati storici RD 2229
   - Validazione carichi unitari

6. **`examples/esempio_dati_storici_rd2229.py`** (NEW)
   - 6 esempi completi d'uso
   - Tabelle e confronti

---

## Riferimenti Bibliografici

- **RD Legge 2229/1939**: Norme Tecniche per le Costruzioni
- **Santarella, L.**: "Il Cemento Armato" (varie edizioni 1930-1970)
- **Giangreco, E.**: Contributi teorici su pressoflessione e taglio

---

## Prossimi Passi

Aggiornamenti futuri possono includere:
1. Tabelle per pilastri a carico di punta
2. Diagrammi di interazione N-M pressoflessione deviata
3. Coefficienti di riduzione per slenderness
4. Formule per verifiche a punzonamento
5. Confronto con norme successive (DM 1992, EC2)
