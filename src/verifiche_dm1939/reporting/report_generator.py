"""
Modulo Report Generator - Generazione report tecnici completi.

Crea relazioni di calcolo dettagliate in formato:
- PDF
- HTML
- Markdown
- DOCX
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from jinja2 import Template
import json


class GeneratoreReport:
    """
    Generatore di report tecnici per verifiche strutturali.
    """
    
    TEMPLATE_HTML = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <title>{{ titolo }}</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
            border-bottom: 2px solid #95a5a6;
            padding-bottom: 5px;
        }
        h3 {
            color: #7f8c8d;
            margin-top: 20px;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #bdc3c7;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #ecf0f1;
        }
        .verificato {
            color: #27ae60;
            font-weight: bold;
        }
        .non-verificato {
            color: #e74c3c;
            font-weight: bold;
        }
        .metadata {
            background-color: #f8f9fa;
            padding: 15px;
            border-left: 4px solid #3498db;
            margin: 20px 0;
        }
        .sezione {
            margin: 30px 0;
            padding: 20px;
            background-color: #ffffff;
            border: 1px solid #dee2e6;
            border-radius: 5px;
        }
        .valore-importante {
            font-weight: bold;
            color: #2980b9;
        }
        .footer {
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #bdc3c7;
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <h1>{{ titolo }}</h1>
    
    <div class="metadata">
        <p><strong>Data:</strong> {{ data }}</p>
        <p><strong>Normativa:</strong> {{ normativa }}</p>
        <p><strong>Metodo di calcolo:</strong> {{ metodo }}</p>
        {% if progettista %}
        <p><strong>Progettista:</strong> {{ progettista }}</p>
        {% endif %}
    </div>
    
    {{ contenuto | safe }}
    
    <div class="footer">
        <p>Generato con Verifiche DM 1939 - Software per verifiche strutturali secondo normativa storica</p>
        <p>{{ data }} - Questo documento è stato generato automaticamente</p>
    </div>
</body>
</html>
"""
    
    TEMPLATE_MARKDOWN = """# {{ titolo }}

**Data:** {{ data }}
**Normativa:** {{ normativa }}
**Metodo di calcolo:** {{ metodo }}
{% if progettista %}**Progettista:** {{ progettista }}{% endif %}

---

{{ contenuto }}

---

*Generato con Verifiche DM 1939 - {{ data }}*
"""
    
    def __init__(self):
        """Inizializza il generatore."""
        self.template_html = Template(self.TEMPLATE_HTML)
        self.template_markdown = Template(self.TEMPLATE_MARKDOWN)
    
    def genera_report_verifica_flessione(
        self,
        risultato: Any,
        sezione: Any,
        materiali: Dict[str, Any],
        sollecitazioni: Dict[str, Any],
    ) -> str:
        """
        Genera contenuto HTML per verifica a flessione.
        
        Args:
            risultato: Risultato verifica flessione
            sezione: Sezione verificata
            materiali: Dizionario materiali
            sollecitazioni: Dizionario sollecitazioni
            
        Returns:
            Contenuto HTML
        """
        stato_classe = "verificato" if risultato.verificato else "non-verificato"
        stato_testo = "VERIFICATA ✓" if risultato.verificato else "NON VERIFICATA ✗"
        
        html = f"""
<div class="sezione">
    <h2>Verifica a Flessione - <span class="{stato_classe}">{stato_testo}</span></h2>
    
    <h3>Dati Geometrici</h3>
    <table>
        <tr>
            <th>Parametro</th>
            <th>Valore</th>
            <th>Unità</th>
        </tr>
        <tr>
            <td>Base sezione</td>
            <td>{sezione.base:.0f}</td>
            <td>mm</td>
        </tr>
        <tr>
            <td>Altezza sezione</td>
            <td>{sezione.altezza:.0f}</td>
            <td>mm</td>
        </tr>
        <tr>
            <td>Altezza utile</td>
            <td>{sezione.altezza_utile:.0f}</td>
            <td>mm</td>
        </tr>
        <tr>
            <td>Copriferro</td>
            <td>{sezione.copriferro:.0f}</td>
            <td>mm</td>
        </tr>
        <tr>
            <td>Area armatura tesa</td>
            <td>{sezione.area_armatura_inferiore:.0f}</td>
            <td>mm²</td>
        </tr>
        <tr>
            <td>Percentuale armatura</td>
            <td>{sezione.percentuale_armatura_meccanica:.2f}</td>
            <td>%</td>
        </tr>
    </table>
    
    <h3>Materiali</h3>
    <table>
        <tr>
            <th>Materiale</th>
            <th>Parametro</th>
            <th>Valore</th>
            <th>Unità</th>
        </tr>
        <tr>
            <td rowspan="2">Calcestruzzo</td>
            <td>Rck</td>
            <td>{materiali['calcestruzzo']['resistenza_caratteristica']:.1f}</td>
            <td>MPa</td>
        </tr>
        <tr>
            <td>σc,amm</td>
            <td>{materiali['calcestruzzo']['tensione_ammissibile_compressione']:.2f}</td>
            <td>MPa</td>
        </tr>
        <tr>
            <td rowspan="2">Acciaio</td>
            <td>Tipo</td>
            <td>{materiali['acciaio']['tipo']}</td>
            <td>-</td>
        </tr>
        <tr>
            <td>σs,amm</td>
            <td>{materiali['acciaio']['tensione_ammissibile']:.1f}</td>
            <td>MPa</td>
        </tr>
    </table>
    
    <h3>Sollecitazioni e Resistenze</h3>
    <table>
        <tr>
            <th>Descrizione</th>
            <th>Valore</th>
            <th>Unità</th>
            <th>Sfruttamento</th>
        </tr>
        <tr>
            <td>Momento sollecitante</td>
            <td class="valore-importante">{sollecitazioni['momento']:.2f}</td>
            <td>kNm</td>
            <td>-</td>
        </tr>
        <tr>
            <td>Momento resistente</td>
            <td class="valore-importante">{risultato.momento_resistente:.2f}</td>
            <td>kNm</td>
            <td>-</td>
        </tr>
        <tr>
            <td>Coefficiente di sicurezza</td>
            <td class="valore-importante">{risultato.coefficiente_sicurezza:.2f}</td>
            <td>-</td>
            <td>-</td>
        </tr>
    </table>
    
    <h3>Tensioni</h3>
    <table>
        <tr>
            <th>Materiale</th>
            <th>Tensione effettiva</th>
            <th>Tensione ammissibile</th>
            <th>Sfruttamento</th>
        </tr>
        <tr>
            <td>Calcestruzzo</td>
            <td>{risultato.tensione_calcestruzzo:.2f} MPa</td>
            <td>{materiali['calcestruzzo']['tensione_ammissibile_compressione']:.2f} MPa</td>
            <td>{risultato.rapporto_sfruttamento_cls*100:.1f}%</td>
        </tr>
        <tr>
            <td>Acciaio</td>
            <td>{risultato.tensione_acciaio:.2f} MPa</td>
            <td>{materiali['acciaio']['tensione_ammissibile']:.1f} MPa</td>
            <td>{risultato.rapporto_sfruttamento_acciaio*100:.1f}%</td>
        </tr>
    </table>
    
    <h3>Asse Neutro</h3>
    <p>Posizione asse neutro dal lembo compresso: <span class="valore-importante">{risultato.posizione_asse_neutro:.1f} mm</span></p>
    <p>Rapporto x/d: <span class="valore-importante">{risultato.posizione_asse_neutro/sezione.altezza_utile:.3f}</span></p>
</div>
"""
        return html
    
    def genera_report_verifica_taglio(
        self,
        risultato: Any,
        sezione: Any,
        materiali: Dict[str, Any],
        sollecitazioni: Dict[str, Any],
    ) -> str:
        """
        Genera contenuto HTML per verifica a taglio.
        
        Args:
            risultato: Risultato verifica taglio
            sezione: Sezione verificata
            materiali: Dizionario materiali
            sollecitazioni: Dizionario sollecitazioni
            
        Returns:
            Contenuto HTML
        """
        stato_classe = "verificato" if risultato.verificato else "non-verificato"
        stato_testo = "VERIFICATA ✓" if risultato.verificato else "NON VERIFICATA ✗"
        
        html = f"""
<div class="sezione">
    <h2>Verifica a Taglio - <span class="{stato_classe}">{stato_testo}</span></h2>
    
    <h3>Sollecitazioni e Resistenze</h3>
    <table>
        <tr>
            <th>Descrizione</th>
            <th>Valore</th>
            <th>Unità</th>
        </tr>
        <tr>
            <td>Taglio sollecitante</td>
            <td class="valore-importante">{sollecitazioni['taglio']:.2f}</td>
            <td>kN</td>
        </tr>
        <tr>
            <td>Taglio resistente totale</td>
            <td class="valore-importante">{risultato.taglio_resistente:.2f}</td>
            <td>kN</td>
        </tr>
        <tr>
            <td>- Contributo calcestruzzo</td>
            <td>{risultato.contributo_calcestruzzo:.2f}</td>
            <td>kN</td>
        </tr>
        <tr>
            <td>- Contributo staffe</td>
            <td>{risultato.contributo_staffe:.2f}</td>
            <td>kN</td>
        </tr>
        <tr>
            <td>- Contributo ferri piegati</td>
            <td>{risultato.contributo_ferri_piegati:.2f}</td>
            <td>kN</td>
        </tr>
        <tr>
            <td>Coefficiente di sicurezza</td>
            <td class="valore-importante">{risultato.coefficiente_sicurezza:.2f}</td>
            <td>-</td>
        </tr>
        <tr>
            <td>Sfruttamento</td>
            <td class="valore-importante">{risultato.rapporto_sfruttamento*100:.1f}%</td>
            <td>%</td>
        </tr>
    </table>
    
    <h3>Armatura Trasversale</h3>
"""
        
        if sezione.staffe:
            html += f"""
    <p><strong>Staffe:</strong></p>
    <ul>
        <li>Diametro: {sezione.staffe.diametro} mm</li>
        <li>Passo: {sezione.staffe.passo} mm</li>
        <li>Numero bracci: {sezione.staffe.numero_bracci}</li>
        <li>Area totale: {sezione.staffe.area_totale:.1f} mm²</li>
    </ul>
"""
        else:
            html += "<p>Nessuna staffa definita</p>"
        
        if sezione.ferri_piegati:
            html += f"""
    <p><strong>Ferri piegati:</strong></p>
    <ul>
        <li>Diametro: {sezione.ferri_piegati.diametro} mm</li>
        <li>Numero: {sezione.ferri_piegati.numero}</li>
        <li>Inclinazione: {sezione.ferri_piegati.inclinazione}°</li>
        <li>Area totale: {sezione.ferri_piegati.area_totale:.1f} mm²</li>
    </ul>
"""
        else:
            html += "<p>Nessun ferro piegato definito</p>"
        
        html += f"""
    <h3>Tensione Tangenziale</h3>
    <p>Tensione tangenziale media: <span class="valore-importante">{risultato.tensione_tangenziale:.3f} MPa</span></p>
    <p>Tensione tangenziale ammissibile cls: <span class="valore-importante">{materiali['calcestruzzo']['tensione_ammissibile_taglio']:.3f} MPa</span></p>
</div>
"""
        return html
    
    def genera_report_completo(
        self,
        risultati: List[Dict[str, Any]],
        filepath: Union[str, Path],
        formato: str = "html",
        titolo: str = "Relazione di Calcolo Strutturale",
        progettista: Optional[str] = None,
        metodo: str = "Santarella",
    ) -> None:
        """
        Genera un report completo e lo salva su file.
        
        Args:
            risultati: Lista di dizionari con risultati verifiche
            filepath: Percorso file output
            formato: "html" o "markdown"
            titolo: Titolo del report
            progettista: Nome progettista
            metodo: Metodo di calcolo utilizzato
        """
        # Prepara metadata
        data = datetime.now().strftime("%d/%m/%Y %H:%M")
        normativa = "DM 2229 del 16 novembre 1939"
        
        # Genera contenuto
        contenuto = ""
        for i, ris in enumerate(risultati, 1):
            tipo_verifica = ris.get("tipo", "generale")
            contenuto += f"<h2>Verifica {i}: {tipo_verifica.upper()}</h2>\n"
            
            if tipo_verifica == "flessione":
                contenuto += self.genera_report_verifica_flessione(
                    ris["risultato"],
                    ris["sezione"],
                    ris["materiali"],
                    ris["sollecitazioni"],
                )
            elif tipo_verifica == "taglio":
                contenuto += self.genera_report_verifica_taglio(
                    ris["risultato"],
                    ris["sezione"],
                    ris["materiali"],
                    ris["sollecitazioni"],
                )
        
        # Renderizza template
        if formato.lower() == "html":
            output = self.template_html.render(
                titolo=titolo,
                data=data,
                normativa=normativa,
                metodo=metodo,
                progettista=progettista,
                contenuto=contenuto,
            )
        elif formato.lower() == "markdown":
            output = self.template_markdown.render(
                titolo=titolo,
                data=data,
                normativa=normativa,
                metodo=metodo,
                progettista=progettista,
                contenuto=contenuto.replace("<table>", "\n").replace("</table>", "\n"),
            )
        else:
            raise ValueError(f"Formato non supportato: {formato}")
        
        # Salva su file
        Path(filepath).write_text(output, encoding="utf-8")
    
    @staticmethod
    def esporta_json(
        risultati: Dict[str, Any],
        filepath: Union[str, Path],
    ) -> None:
        """
        Esporta risultati in formato JSON.
        
        Args:
            risultati: Dizionario con risultati
            filepath: Percorso file output
        """
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(risultati, f, indent=2, ensure_ascii=False)
