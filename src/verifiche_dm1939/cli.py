"""
Interfaccia a riga di comando (CLI) per verifiche strutturali DM 1939.

Utilizzo:
    python -m verifiche_dm1939.cli trave --config config/trave_esempio.yaml
    python -m verifiche_dm1939.cli pilastro --config config/pilastro_esempio.yaml
    python -m verifiche_dm1939.cli batch --csv data/travi_esempio.csv
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from verifiche_dm1939.core.config import Config
from verifiche_dm1939.materials.calcestruzzo import Calcestruzzo
from verifiche_dm1939.materials.acciaio import Acciaio
from verifiche_dm1939.sections.sezione_rettangolare import SezioneRettangolare
from verifiche_dm1939.verifications.verifica_flessione import VerificaFlessione
from verifiche_dm1939.verifications.verifica_taglio import VerificaTaglio
from verifiche_dm1939.verifications.verifica_pressoflessione import (
    VerificaPressoflessioneRetta,
    VerificaPressoflessioneDeviata,
)
from verifiche_dm1939.io_handlers.csv_handler import CSVHandler
from verifiche_dm1939.reporting.grafici import GeneratoreGrafici
from verifiche_dm1939.reporting.report_generator import GeneratoreReport


def verifica_trave_da_config(config_path: Path, output_dir: Optional[Path] = None) -> None:
    """
    Esegue verifica trave da file di configurazione.
    
    Args:
        config_path: Percorso file YAML configurazione
        output_dir: Directory output (default: output/)
    """
    # Carica configurazione
    config = Config.from_yaml(config_path)
    
    # Crea materiali
    calcestruzzo = Calcestruzzo(
        resistenza_caratteristica=config.calcestruzzo.rck,
        calcola_auto=config.calcestruzzo.calcola_auto,
    )
    
    acciaio = Acciaio.da_tipo(config.acciaio.tipo) if config.acciaio.tipo else Acciaio(
        tipo="Custom",
        tensione_snervamento=config.acciaio.tensione_snervamento,
        calcola_auto=config.acciaio.calcola_auto,
    )
    
    # Crea sezione
    sezione = SezioneRettangolare(
        base=config.sezione.base,
        altezza=config.sezione.altezza,
        copriferro=config.sezione.copriferro,
    )
    
    # Aggiungi armature
    if "longitudinale" in config.armatura.__dict__:
        arm_long = config.armatura.longitudinale
        if "diametro_inferiore" in arm_long and "numero_barre_inferiori" in arm_long:
            sezione.aggiungi_armatura_inferiore(
                diametro=arm_long["diametro_inferiore"],
                numero_barre=arm_long["numero_barre_inferiori"],
            )
        if "diametro_superiore" in arm_long and "numero_barre_superiori" in arm_long:
            sezione.aggiungi_armatura_superiore(
                diametro=arm_long["diametro_superiore"],
                numero_barre=arm_long["numero_barre_superiori"],
            )
    
    if "trasversale" in config.armatura.__dict__:
        arm_trasv = config.armatura.trasversale
        if "diametro" in arm_trasv and "passo" in arm_trasv:
            sezione.aggiungi_staffe(
                diametro=arm_trasv["diametro"],
                passo=arm_trasv["passo"],
                numero_bracci=arm_trasv.get("bracci", 2),
            )
    
    # Esegui verifiche
    print("\n" + "="*70)
    print("VERIFICA TRAVE - DM 2229/1939")
    print("="*70 + "\n")
    
    # Verifica flessione
    if config.sollecitazioni.momento_flettente > 0:
        print("VERIFICA A FLESSIONE")
        verifica_fless = VerificaFlessione(
            sezione=sezione,
            calcestruzzo=calcestruzzo,
            acciaio=acciaio,
            momento_flettente=config.sollecitazioni.momento_flettente,
        )
        risultato_fless = verifica_fless.verifica()
        print(risultato_fless.genera_report_breve())
    
    # Verifica taglio
    if config.sollecitazioni.taglio > 0:
        print("VERIFICA A TAGLIO")
        verifica_tagl = VerificaTaglio(
            sezione=sezione,
            calcestruzzo=calcestruzzo,
            acciaio=acciaio,
            taglio=config.sollecitazioni.taglio,
            metodo=config.opzioni_calcolo.metodo.value,
        )
        risultato_tagl = verifica_tagl.verifica()
        print(risultato_tagl.genera_report_breve())
    
    # Genera output se richiesto
    if output_dir and config.opzioni_calcolo.genera_grafici:
        output_dir.mkdir(exist_ok=True, parents=True)
        
        generatore = GeneratoreGrafici()
        fig = generatore.disegna_sezione(sezione, titolo="Sezione Trave")
        generatore.salva_grafico(fig, output_dir / "sezione.png")
        
        print(f"\nGrafici salvati in: {output_dir}")


def verifica_pilastro_da_config(config_path: Path, output_dir: Optional[Path] = None) -> None:
    """
    Esegue verifica pilastro da file di configurazione.
    
    Args:
        config_path: Percorso file YAML configurazione
        output_dir: Directory output
    """
    config = Config.from_yaml(config_path)
    
    # Simile a verifica_trave_da_config ma con verifiche a pressoflessione
    print("\n" + "="*70)
    print("VERIFICA PILASTRO - DM 2229/1939")
    print("="*70 + "\n")
    print("Funzionalità in sviluppo...")


def main() -> None:
    """Entry point CLI."""
    parser = argparse.ArgumentParser(
        description="Verifiche strutturali secondo DM 2229/1939",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest="comando", help="Comando da eseguire")
    
    # Comando: trave
    parser_trave = subparsers.add_parser("trave", help="Verifica trave")
    parser_trave.add_argument("--config", type=Path, required=True, help="File configurazione YAML")
    parser_trave.add_argument("--output", type=Path, help="Directory output")
    
    # Comando: pilastro
    parser_pilastro = subparsers.add_parser("pilastro", help="Verifica pilastro")
    parser_pilastro.add_argument("--config", type=Path, required=True, help="File configurazione YAML")
    parser_pilastro.add_argument("--output", type=Path, help="Directory output")
    
    # Comando: batch
    parser_batch = subparsers.add_parser("batch", help="Verifica batch da CSV")
    parser_batch.add_argument("--csv", type=Path, required=True, help="File CSV con dati")
    parser_batch.add_argument("--output", type=Path, help="Directory output")
    
    # Comando: template
    parser_template = subparsers.add_parser("template", help="Genera template CSV")
    parser_template.add_argument("--tipo", choices=["trave", "pilastro"], required=True)
    parser_template.add_argument("--output", type=Path, required=True, help="File output")
    
    args = parser.parse_args()
    
    if not args.comando:
        parser.print_help()
        return
    
    try:
        if args.comando == "trave":
            verifica_trave_da_config(args.config, args.output)
        elif args.comando == "pilastro":
            verifica_pilastro_da_config(args.config, args.output)
        elif args.comando == "batch":
            print("Funzionalità batch in sviluppo...")
        elif args.comando == "template":
            CSVHandler.genera_template_csv(args.output, args.tipo)
            print(f"Template generato: {args.output}")
    
    except Exception as e:
        print(f"\nERRORE: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
