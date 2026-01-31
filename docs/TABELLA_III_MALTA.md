# Tabella III Malta - Quantitativi Cemento e Sabbia

## Fonte

**Regio Decreto Legge n. 2229 del 16 novembre 1939**
- Pagine 6-7 (Tabella III ruotata 90° antiorario)
- Prontuario dell'Ing. Luigi Santarella
- "Quantitativi di cemento e sabbia per 1 m³ di malta"

---

## Tabella III - Dati Completi

| Rapporto A/C | Cemento (kg/m³) | Sabbia (kg/m³) | Peso Specifico Apparente (kg/m³) |
|--------------|-----------------|----------------|----------------------------------|
| 1:1          | 1050            | 900            | 1100                             |
| 1:1.40       | 800             | 1080           | 1080                             |
| 1:1.85       | 715             | 1215           | 1080                             |
| 1:2.30       | 685             | 1405           | 1080                             |
| 1:2.70       | 625             | 1520           | 1100                             |
| 1:3.70       | 385             | 1530           | 1070                             |

---

## Interpretazione dei Dati

### Rapporto A/C (Cemento : Sabbia)

- **1:1** = 1 parte di cemento per 1 parte di sabbia
  - Composizione molto ricca di cemento
  - Resistenza molto alta
  - Usato per malte molto resistenti

- **1:2.30** = 1 parte di cemento per 2.30 parti di sabbia
  - Composizione equilibrata
  - Resistenza media
  - Usato per intonaci normali

- **1:3.70** = 1 parte di cemento per 3.70 parti di sabbia
  - Composizione povera di cemento
  - Resistenza bassa
  - Usato per malte economiche, camici

### Quantitativi per Metro Cubo

**Esempio: Malta 1:1.85 (media-alta resistenza)**
- Cemento: 715 kg/m³
- Sabbia: 1215 kg/m³
- **Peso totale malta:** 1080 kg/m³ (peso specifico apparente)

Nota: 715 + 1215 = 1930 kg, ma il peso specifico è 1080 kg/m³ per via della porosità e dell'aria incorporata nella malta.

---

## Utilizzi Tipici

| Uso | Rapporto A/C | Caratteristiche |
|-----|--------------|-----------------|
| **Intonaco di finitura** | 1:2.70 a 1:3.70 | Economico, facile da stendere |
| **Intonaco di base** | 1:2.30 a 1:2.70 | Resistente, media durabilità |
| **Malta di allettamento** | 1:2.30 | Buona aderenza, resistenza |
| **Malta per muratura** | 1:2.30 a 1:3.70 | Economica, buona lavorabilità |
| **Malta da sigillo** | 1:1.40 a 1:1.85 | Resistente, buona aderenza |
| **Malta per riprese** | 1:1 a 1:1.40 | Molto resistente, per zone critiche |

---

## Calcolo Quantitativi

### Formula Base

Per qualsiasi volume V di malta:

$$Q_{cemento} = \sigma_{c} \times V$$
$$Q_{sabbia} = \sigma_{s} \times V$$

Dove:
- σc = kg di cemento per m³
- σs = kg di sabbia per m³
- V = volume in m³

### Esempio: Intonaco 100 m² con spessore 2 cm

**Dati:**
- Superficie: 100 m²
- Spessore: 2 cm = 0.02 m
- Volume malta: 100 × 0.02 = 2.0 m³
- Rapporto A/C: 1:2.30

**Calcolo:**
- Cemento: 685 kg/m³ × 2.0 m³ = **1.370 kg** (ca. 27 sacchi da 50 kg)
- Sabbia: 1.405 kg/m³ × 2.0 m³ = **2.810 kg**
- Peso totale: 1.080 kg/m³ × 2.0 m³ = **2.160 kg**

---

## Interpolazione per Rapporti Intermedi

La tabella è implementata con interpolazione lineare per rapporti non tabulati:

| Rapporto A/C | Cemento (kg/m³) | Sabbia (kg/m³) | Metodo |
|--------------|-----------------|----------------|--------|
| 1.00         | 1050            | 900            | Tabulato |
| 1.20         | 925             | 990            | Interpolato |
| 1.50         | 781             | 1110           | Interpolato |
| 1.75         | 734             | 1185           | Interpolato |
| 2.00         | 705             | 1278           | Interpolato |
| 2.50         | 655             | 1462           | Interpolato |
| 3.00         | 553             | 1523           | Interpolato |
| 3.70         | 385             | 1530           | Tabulato |

---

## Resa della Malta

### Riduzione di Volume

La malta confezionata ha una **resa inferiore** al volume teorico a causa di:
- **Assestamento** durante la stesa
- **Aria incorporata** durante la miscelazione
- **Porosità** della malta indurita

**Resa tipica: 85-95% del volume teorico**
- Con vibrazione: 90-95%
- Con stesa manuale: 85-90%

### Esempio di Resa

Per 1 m³ di malta teorica con resa 87%:
- Volume effettivo: 0.87 m³
- Cemento necessario: 715 kg/m³ × 0.87 = **622 kg**
- Sabbia necessaria: 1215 kg/m³ × 0.87 = **1.057 kg**

---

## Conversion in Unità Moderne

### Conversione Volume

| Unità Storica | Unità Moderna |
|---------------|--------------|
| 1 m³ | 1.000 litri |
| 1 m³ | 1 m³ |
| kg/m³ | kg/m³ (identico) |

### Densità Comparata

| Malta Epoca | Peso spec. app. | Densità moderna equivalente |
|------------|-----------------|------------------------------|
| 1:1        | 1100 kg/m³      | Malta ad alta resistenza |
| 1:1.85     | 1080 kg/m³      | Malta media resistenza |
| 1:2.30     | 1080 kg/m³      | Malta ordinaria |
| 1:3.70     | 1070 kg/m³      | Malta economica |

---

## Implementazione nel Codice

### Modulo: `tabella_malta.py`

```python
from verifiche_dm1939.core.tabella_malta import (
    TABELLA_III_MALTA,
    get_malta_da_rapporto,
    interpola_dosatura_malta,
    calcola_malta_per_volume,
    genera_tabella_malta_testo,
    genera_tabella_malta_html,
)
```

### Esempi di Utilizzo

**Consultazione rapporto tabulato:**
```python
dosatura = get_malta_da_rapporto("1:1.85")
print(f"Cemento: {dosatura.cemento_kg} kg/m³")
print(f"Sabbia: {dosatura.sabbia_kg} kg/m³")
```

**Interpolazione per rapporto intermedio:**
```python
dosatura = interpola_dosatura_malta(1.50)
print(f"Cemento: {dosatura['cemento_kg']:.0f} kg/m³")
```

**Calcolo per volume specifico:**
```python
quantitativo = calcola_malta_per_volume(2.30, 2.0)  # 2.30 = A/C, 2.0 = m³
print(f"Cemento totale: {quantitativo['cemento_kg']:.0f} kg")
```

---

## Note Storiche

- **Periodo:** 1930-1970 (Prontuari Santarella)
- **Normativa:** RD 2229/1939
- **Metodo:** Miscela per volume (non per peso)
- **Sabbia:** Sempre considerata "media" (grana 0.5-5 mm tipicamente)
- **Acqua:** Non inclusa nella tabella (dosata a vista/esperienza)
- **Rapporto A/C:** Storico, da non confondere con acqua/cemento

---

## Prossimi Passi

- Implementazione di formule per malte speciali (calce, pozzolanica)
- Correzioni per aggregati di granulometria diversa
- Tabelle per mortar époque (calce + cemento)
- Integrazione con verifiche di aderenza
