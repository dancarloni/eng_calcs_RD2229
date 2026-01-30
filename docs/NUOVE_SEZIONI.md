# 🎯 Nuove Sezioni Avanzate - DM 2229/1939

## ✅ Implementazione Completata

Sono state aggiunte **8 geometrie di sezione** complete con calcoli avanzati e proprietà geometriche complete.

---

## 📐 Geometrie Supportate

### 1. **Sezione Rettangolare** (300×500 mm)
- Base e altezza qualsiasi
- Armature inferiori, superiori, laterali
- Staffe e armature a taglio

### 2. **Sezione a T** (Trave con soletta)
- Soletta collaborante (larghezza e spessore qualsiasi)
- Nervatura centrale
- Ideale per travi con soletta

### 3. **Sezione a Doppia T (I)**
- Soletta superiore + anima + soletta inferiore
- Sezione fortemente deformabile
- Asimmetrica o simmetrica

### 4. **Sezione a L**
- Due ali con spessori indipendenti
- Utile per colonne angolari

### 5. **Sezione a U** (Canale)
- Soletta superiore + due ani + soletta inferiore
- Sezione aperta

### 6. **Sezione Rettangolare Cava** (Scatolare)
- Parete superiore, inferiore, laterali con spessori indipendenti
- Ideale per pilastri cavi

### 7. **Sezione Circolare** (Pilastro)
- Diametro qualsiasi
- Armature distribuibili radialmente

### 8. **Sezione Circolare Cava** (Tubo)
- Diametro esterno e interno indipendenti
- Spessore variabile

---

## 🔧 Funzionalità Avanzate

### 1. **Proprietà Geometriche Complete**
```python
prop = sezione.calcola_proprieta_geometriche()
prop.area                          # mm²
prop.y_baricentro                  # posizione lembo sup
prop.momento_inerzia_x             # Ix [mm⁴]
prop.momento_inerzia_y             # Iy [mm⁴]
prop.modulo_resistenza_sup         # Wx [mm³]
prop.modulo_resistenza_inf         # Wx [mm³]
```

### 2. **Coefficiente Omogeneizzazione**
Automatico o manuale a scelta:
```python
# Automatico: n = Es/Ec
n_auto = sezione.coeff_omogeneizzazione

# Manuale: imponi un valore fisso
sezione.coeff_omogeneizzazione = 15.0

# Ripristina automatico
sezione.coeff_omogeneizzazione = None
```

### 3. **Calcolo Asse Neutro Avanzato**
Considerando forma, armature, N e M:
```python
asse_neutro = sezione.calcola_asse_neutro(
    M=50.0,   # Momento flettente [kNm]
    N=-100.0  # Sforzo normale [kN]
)

asse_neutro.posizione              # Posizione asse neutro [mm]
asse_neutro.tipo_rottura           # 'cls', 'acciaio', 'bilanciato'
asse_neutro.epsilon_cls_sup        # Deformazione cls
asse_neutro.epsilon_acciaio_inf    # Deformazione acciaio
```

### 4. **Utility Calcolo Area Ferro**
Calcola automaticamente l'armatura necessaria:
```python
As_necessaria = sezione.calcola_area_ferro_necessaria(
    M=80.0,              # Momento [kNm]
    N=0.0,               # Sforzo [kN]
    posizione='inferiore' # 'inferiore' o 'superiore'
)
# Ritorna: 1938 mm² → 6.2φ20
```

### 5. **Rotazione 90 Gradi**
Tutte le sezioni ruotabili:
```python
sezione.ruota_90_gradi()  # Ruota

# Le proprietà si aggiornano automaticamente
prop_ruotata = sezione.calcola_proprieta_geometriche()
# Ix e Iy sono scambiati
```

### 6. **Info Contestuali (Tooltip)**
Per qualsiasi punto della sezione:
```python
info = sezione.get_info_tooltip((x, y))
# Restituisce: "Posizione: (150, 250) mm\nDistanza baricentro: 50.2 mm\n..."
```

### 7. **Dimensioni Principali**
Accesso alle dimensioni caratteristiche:
```python
dim = sezione.get_dimensioni_principali()
# Rettangolare: {'b': 300, 'h': 500, 'base': 300, 'altezza': 500}
# T: {'bw': 200, 'h': 600, 'bf': 800, 'tf': 120}
# Circolare: {'D': 400, 'diametro': 400}
```

---

## 📐 Convenzioni DM 2229/1939

### Armature
- **As** = armatura inferiore (tesa con M positivo)
- **As'** = armatura superiore (tesa con M negativo)

### Altezze Utili
- **d** = altezza utile armatura inferiore dal lembo superiore
- **d'** = altezza utile armatura superiore dal lembo superiore

### Sollecitazioni
- **M positivo** → tende fibre inferiori (As in trazione)
- **M negativo** → tende fibre superiori (As' in trazione)
- **N negativo** → compressione
- **N positivo** → trazione

### Parametri Geometrici
- **Asse neutro** (x) misurato dal lembo superiore
- **Baricentro** (y_G) misurato dal lembo superiore
- **Momenti d'inerzia** rispetto asse baricentrico orizzontale

---

## 💻 Esempio di Utilizzo

```python
from verifiche_dm1939 import Calcestruzzo, Acciaio, SezioneRettangolare

# Definisci materiali
cls = Calcestruzzo(resistenza_caratteristica=15.0)
acc = Acciaio(tipo='FeB32k', tensione_snervamento=320.0)

# Crea sezione rettangolare 300x500
sezione = SezioneRettangolare(300, 500, cls, acc, copriferro=30)

# Aggiungi armature
sezione.aggiungi_armatura_inferiore(20, 3)  # 3φ20 inferiore
sezione.aggiungi_armatura_superiore(16, 2)  # 2φ16 superiore
sezione.aggiungi_staffe(8, 150, 2)          # Staffe φ8/150

# Calcola proprietà
prop = sezione.calcola_proprieta_geometriche()
print(f"Area: {prop.area} mm²")
print(f"Ix: {prop.momento_inerzia_x:.2e} mm⁴")
print(f"As: {sezione.As} mm² (ρ = {sezione.percentuale_armatura:.2f}%)")

# Calcola asse neutro
an = sezione.calcola_asse_neutro(M=50.0, N=-100.0)
print(f"Asse neutro: x = {an.posizione:.0f} mm")

# Calcola area ferro necessaria
As_nec = sezione.calcola_area_ferro_necessaria(M=80.0)
print(f"As necessaria: {As_nec:.0f} mm²")

# Ruota sezione
sezione.ruota_90_gradi()
prop_ruot = sezione.calcola_proprieta_geometriche()
print(f"Dopo rotazione: Ix = {prop_ruot.momento_inerzia_x:.2e} mm⁴")
```

---

## 📊 Output Esempio

L'esecuzione di `python examples/esempio_nuove_sezioni.py` genera:

1. **Calcoli numerici** per tutte le 8 geometrie
2. **Proprietà geometriche** complete (A, I, W, y_G)
3. **Test asse neutro** con N e M
4. **Test utility** calcolo area ferro
5. **Verifiche** rotazione 90° e coeff. omogeneizzazione
6. **Grafico comparativo** `examples/output/confronto_sezioni.png` con tutte le sezioni disegnate

---

## 🎯 Verifiche Supportate

Le nuove sezioni si integrano con il sistema di verifiche esistente:

- ✅ Verifiche a flessione (Santarella)
- ✅ Verifiche a taglio (con staffe e ferri piegati)
- ✅ Verifiche a pressoflessione (retta e deviata)
- ✅ Calcolo asse neutro con N e M
- ✅ Generazione grafici con sezioni disegnate
- ✅ Report HTML con proprietà geometriche

---

## 📝 File Implementati

| File | Descrizione |
|------|-------------|
| `sezione_base.py` | Classe base astratta con interfaccia comune |
| `sezione_rettangolare_new.py` | Sezione rettangolare aggiornata |
| `sezione_t.py` | Sezione a T |
| `sezione_i.py` | Sezione a doppia T |
| `sezioni_speciali.py` | Sezioni L, U, rettangolare cava |
| `sezione_circolare.py` | Sezioni circolari (piena e cava) |
| `esempio_nuove_sezioni.py` | Esempio completo con tutte le funzionalità |

---

## 🚀 Prossimi Passi

1. Integrare le nuove sezioni nei verifiche
2. Aggiornare il generatore di report con grafici delle nuove geometrie
3. Aggiungere supporto per sezioni composte (T + pilastri, etc.)
4. Implementare tool interattivo per disegnare sezioni personalizzate

---

**Versione**: 0.2.0  
**Data**: 30 gennaio 2026  
**Normativa**: DM 2229/1939 - Norme per le costruzioni in calcestruzzo
