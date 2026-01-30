"""
Esempio completo di utilizzo del software per verifica di una trave.

Questo esempio dimostra:
- Definizione materiali
- Creazione sezione con armature
- Verifica a flessione
- Verifica a taglio
- Generazione grafici
- Generazione report
"""

from pathlib import Path
import sys

# Aggiungi src al path per import
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from verifiche_dm1939.materials.calcestruzzo import Calcestruzzo
from verifiche_dm1939.materials.acciaio import Acciaio
from verifiche_dm1939.sections.sezione_rettangolare import SezioneRettangolare
from verifiche_dm1939.verifications.verifica_flessione import VerificaFlessione
from verifiche_dm1939.verifications.verifica_taglio import VerificaTaglio
from verifiche_dm1939.reporting.grafici import GeneratoreGrafici
from verifiche_dm1939.reporting.report_generator import GeneratoreReport


def esempio_trave_semplice():
    """
    Esempio di verifica di una trave in c.a. secondo DM 2229/1939.
    
    Dati:
    - Trave 300x500 mm
    - Calcestruzzo Rck 15 MPa
    - Acciaio FeB32k
    - Momento 80 kNm, Taglio 50 kN
    """
    print("="*70)
    print("ESEMPIO: Verifica Trave in Calcestruzzo Armato")
    print("Normativa: DM 2229/1939 - Metodo Santarella")
    print("="*70)
    print()
    
    # 1. DEFINIZIONE MATERIALI
    print("1. Definizione materiali...")
    
    # Calcestruzzo Rck 15 MPa
    calcestruzzo = Calcestruzzo(
        resistenza_caratteristica=15.0,  # MPa
        calcola_auto=True  # Calcola automaticamente tensioni ammissibili
    )
    print(f"   {calcestruzzo}")
    
    # Acciaio FeB32k
    acciaio = Acciaio.da_tipo("FeB32k")
    print(f"   {acciaio}")
    print()
    
    # 2. CREAZIONE SEZIONE
    print("2. Creazione sezione...")
    
    sezione = SezioneRettangolare(
        base=300,  # mm
        altezza=500,  # mm
        copriferro=30  # mm
    )
    
    # Aggiungi armatura longitudinale inferiore (tesa)
    sezione.aggiungi_armatura_inferiore(
        diametro=16,  # mm - 4φ16
        numero_barre=4
    )
    
    # Aggiungi armatura longitudinale superiore (compressa/staffaggio)
    sezione.aggiungi_armatura_superiore(
        diametro=12,  # mm - 2φ12
        numero_barre=2
    )
    
    # Aggiungi staffe
    sezione.aggiungi_staffe(
        diametro=8,  # mm
        passo=200,  # mm
        numero_bracci=2
    )
    
    print(f"   {sezione}")
    print(f"   Altezza utile: {sezione.altezza_utile:.1f} mm")
    print(f"   Area armatura tesa: {sezione.area_armatura_inferiore:.0f} mm²")
    print(f"   Percentuale armatura: {sezione.percentuale_armatura_meccanica:.2f}%")
    print()
    
    # 3. VERIFICA A FLESSIONE
    print("3. Verifica a flessione...")
    
    momento = 80.0  # kNm
    
    verifica_fless = VerificaFlessione(
        sezione=sezione,
        calcestruzzo=calcestruzzo,
        acciaio=acciaio,
        momento_flettente=momento
    )
    
    risultato_fless = verifica_fless.verifica()
    print(risultato_fless.genera_report_breve())
    
    # 4. VERIFICA A TAGLIO
    print("4. Verifica a taglio...")
    
    taglio = 50.0  # kN
    
    verifica_tagl = VerificaTaglio(
        sezione=sezione,
        calcestruzzo=calcestruzzo,
        acciaio=acciaio,
        taglio=taglio,
        considera_calcestruzzo=True,
        metodo="santarella"
    )
    
    risultato_tagl = verifica_tagl.verifica()
    print(risultato_tagl.genera_report_breve())
    
    # 5. GENERAZIONE GRAFICI
    print("5. Generazione grafici...")
    
    generatore_grafici = GeneratoreGrafici()
    
    # Crea directory output
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    # Disegna sezione
    fig_sezione = generatore_grafici.disegna_sezione(
        sezione=sezione,
        asse_neutro=risultato_fless.posizione_asse_neutro,
        titolo="Sezione Trave 300x500 mm"
    )
    generatore_grafici.salva_grafico(fig_sezione, output_dir / "sezione_trave.png")
    print(f"   Salvato: {output_dir / 'sezione_trave.png'}")
    
    # Diagramma tensioni
    fig_tensioni = generatore_grafici.diagramma_tensioni_flessione(
        sezione=sezione,
        sigma_c=risultato_fless.tensione_calcestruzzo,
        sigma_s=risultato_fless.tensione_acciaio,
        x=risultato_fless.posizione_asse_neutro,
        sigma_c_amm=calcestruzzo.tensione_ammissibile_compressione,
        sigma_s_amm=acciaio.tensione_ammissibile,
    )
    generatore_grafici.salva_grafico(fig_tensioni, output_dir / "tensioni_flessione.png")
    print(f"   Salvato: {output_dir / 'tensioni_flessione.png'}")
    
    # Dominio M-N
    fig_dominio = generatore_grafici.dominio_momento_sforzo_normale(
        base=sezione.base,
        altezza=sezione.altezza,
        area_armatura_inf=sezione.area_armatura_inferiore,
        area_armatura_sup=sezione.area_armatura_superiore,
        sigma_c_amm=calcestruzzo.tensione_ammissibile_compressione,
        sigma_s_amm=acciaio.tensione_ammissibile,
    )
    generatore_grafici.salva_grafico(fig_dominio, output_dir / "dominio_MN.png")
    print(f"   Salvato: {output_dir / 'dominio_MN.png'}")
    print()
    
    # 6. GENERAZIONE REPORT HTML
    print("6. Generazione report HTML...")
    
    generatore_report = GeneratoreReport()
    
    risultati = [
        {
            "tipo": "flessione",
            "risultato": risultato_fless,
            "sezione": sezione,
            "materiali": {
                "calcestruzzo": calcestruzzo.to_dict(),
                "acciaio": acciaio.to_dict(),
            },
            "sollecitazioni": {"momento": momento},
        },
        {
            "tipo": "taglio",
            "risultato": risultato_tagl,
            "sezione": sezione,
            "materiali": {
                "calcestruzzo": calcestruzzo.to_dict(),
                "acciaio": acciaio.to_dict(),
            },
            "sollecitazioni": {"taglio": taglio},
        },
    ]
    
    generatore_report.genera_report_completo(
        risultati=risultati,
        filepath=output_dir / "relazione_calcolo.html",
        formato="html",
        titolo="Relazione di Calcolo - Trave in C.A.",
        progettista="Ing. Esempio",
        metodo="Santarella"
    )
    print(f"   Salvato: {output_dir / 'relazione_calcolo.html'}")
    print()
    
    print("="*70)
    print("ESEMPIO COMPLETATO CON SUCCESSO!")
    print(f"I file sono stati salvati in: {output_dir}")
    print("="*70)


if __name__ == "__main__":
    esempio_trave_semplice()
