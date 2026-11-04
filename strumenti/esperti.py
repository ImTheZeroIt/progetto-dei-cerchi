"""Schede per esperti: una pagina per materia, da testi/it/esperti/*.json.

Ogni scheda dice a chi è rivolta, perché serve quella competenza, come funzionano le regole,
che cosa è cambiato di recente, quali numeri vanno verificati, le domande e gli articoli da leggere.
Le pagine si costruiscono in docs/esperti/ e si possono mandare a chiunque con un link.
"""
import glob
import html
import json
import os
import re
from urllib.parse import quote

E = html.escape
REPOSITORY = "https://github.com/ImTheZeroIt/progetto-dei-cerchi"
CONTATTO = "zerocirclesproject@gmail.com"

NOMI = {"costituzione": "Costituzione", "codice-01-annex-a": "Allegato A al Codice 1",
        "codice-16-allegato-a": "Allegato A al Codice 16", "codice-16-allegato-b": "Allegato B al Codice 16",
        "codice-16-allegato-c": "Allegato C al Codice 16"}

PROGETTO = ("Il Progetto dei Cerchi è una proposta aperta per organizzare la vita in comune senza denaro "
            "interno e senza un potere centrale: decidono le persone in assemblea, il lavoro necessario a tutti "
            "è diviso a rotazione, i beni essenziali si prendono gratis dai Magazzini comuni secondo il bisogno. "
            "È scritto per intero, in una Costituzione e in sedici Codici, ma non è in vigore da nessuna parte "
            "e non è mai stato sperimentato. Per questo servono persone competenti che dicano dove le regole "
            "non reggono.")

GLOSSARIO = [
    ("Cerchio 0 — Nucleo di Cura", "il gruppo di convivenza, da 1 a 15 persone: casa, cura quotidiana, ospitalità."),
    ("Cerchio 1 — Comunità di Base", "di norma 30–500 persone; decide in Assemblea, organizza il lavoro e il Magazzino."),
    ("Cerchi 2, 3 e 4", "livelli più ampi (Bacino, Bioregione, Cerchio globale) che coordinano e non comandano."),
    ("CBO — Contributo di Base Obbligatorio", "il lavoro necessario a tutti, a rotazione tra chi può: in media non oltre 15 ore a settimana."),
    ("Magazzini Comuni e Paniere", "da lì si prendono gratis, secondo il bisogno, i beni essenziali (il Paniere)."),
    ("CdR — Contributo di Riconoscenza", "riconoscimento personale del lavoro oltre il CBO; dà precedenza su pochi beni non essenziali; non è denaro."),
    ("UCR — Unità di Costo di Riproduzione", "il costo di un bene espresso in ore di lavoro, materiali ed energia; serve a fissare le soglie delle decisioni."),
    ("STV — Scheda Tecnica di Validazione", "la scheda che dice come un bene, un'attività o un sistema va fatto e controllato."),
    ("Consigli tecnici, Cerchio di Garanzia", "piccoli organi di persone sorteggiate tra chi ha le competenze, con incarichi brevi; propongono e controllano, l'Assemblea decide."),
    ("L1, L2, L3", "i tre livelli di validazione delle competenze, secondo il rischio del compito (Codice 5)."),
]


def nome_testo(f):
    return NOMI.get(f) or "Codice %d" % int(f.split("-")[1])


def ancore(sito_dir, f):
    """Numero d'articolo -> id del titolo nella pagina del registro."""
    p = os.path.join(sito_dir, "registro", f + ".html")
    if not os.path.exists(p):
        return {}
    t = open(p, encoding="utf-8").read()
    return {m.group(2): m.group(1) for m in re.finditer(r'<h[2-4] id="(art-([0-9]+(?:-[a-z]+)?)--[^"]*)"', t)}


def da_leggere(scheda, sito_dir):
    voci = []
    for t in scheda["testi"]:
        f = t["file"]
        pagina = "../registro/%s.html" % f
        if t["articoli"] == "tutti":
            voci.append('<li><a href="%s"><strong>%s</strong></a>: tutto il testo</li>' % (pagina, nome_testo(f)))
            continue
        a = ancore(sito_dir, f)
        arts = ", ".join('<a href="%s#%s">%s</a>' % (pagina, a[n], E(n)) if n in a else E(n) for n in t["articoli"])
        voci.append('<li><a href="%s"><strong>%s</strong></a>: art. %s</li>' % (pagina, nome_testo(f), arts))
    return "<ul>%s</ul>" % "".join(voci)


def rispondere(scheda):
    titolo = "[Esperti — %s] " % scheda["titolo"]
    corpo = ("Scheda: %s\nDomanda n.: \n\nRisposta o osservazione:\n\n"
             "(Se volete, indicate la vostra competenza: aiuta a valutare la risposta.)" % scheda["titolo"])
    issue = "%s/issues/new?title=%s&body=%s" % (REPOSITORY, quote(titolo), quote(corpo))
    mail = "mailto:%s?subject=%s" % (CONTATTO, quote("Scheda per esperti — " + scheda["titolo"]))
    return ("<p>Non serve rispondere a tutto: anche una sola domanda aiuta. Indicate il numero della domanda, "
            "e se una domanda è sbagliata o mal posta ditelo: è un'informazione utile anche quella.</p>"
            '<ul><li><a href="%s">Apri una segnalazione su GitHub</a> (serve un account gratuito; le risposte sono pubbliche)</li>'
            '<li>oppure scrivete a <a href="%s">%s</a>: va bene anche una riga</li></ul>'
            "<p>Ogni risposta viene letta. Se porta a cambiare una regola, la modifica è registrata con la data e la ragione "
            'nel <a href="../registro/modifiche.html">registro delle modifiche</a>.</p>' % (E(issue), E(mail), CONTATTO))


def pagina_scheda(s, sito_dir, versione):
    p = []
    p.append('<p class="briciole"><a href="../index.html">Progetto dei Cerchi</a> · <a href="index.html">Schede per esperti</a></p>')
    p.append('<p><strong>Per:</strong> %s.</p>' % E(s["a_chi"]))
    p.append('<p class="piccolo">Scheda aggiornata al %s, sui testi della Costituzione %s e dei Codici in vigore in quella data.</p>'
             % (data_it(s.get("aggiornata", "")), E(versione)))
    p.append('<h2 id="progetto">Il progetto in breve</h2><p>%s</p>' % PROGETTO)
    p.append('<details class="allineamento"><summary>Le parole del progetto</summary><ul>%s</ul></details>'
             % "".join("<li><strong>%s</strong>: %s</li>" % (E(a), E(b)) for a, b in GLOSSARIO))
    p.append('<h2 id="perche">Perché chiediamo il vostro parere</h2><p>%s</p>' % E(s["perche"]))
    p.append('<h2 id="come-funziona">Come funziona, in breve</h2><ul>%s</ul>' % "".join("<li>%s</li>" % E(x) for x in s["come_funziona"]))
    if s.get("modifiche_recenti"):
        p.append('<h2 id="modifiche">Che cosa è cambiato di recente</h2><p>Modifiche di ottobre e novembre 2026 che toccano questa materia.</p><ul>%s</ul>'
                 % "".join("<li>%s</li>" % E(x) for x in s["modifiche_recenti"]))
    righe = "".join("<li><p><strong>%s</strong> <span class=\"piccolo\">(%s)</span></p><p>%s</p></li>" % (E(n["valore"]), E(n["dove"]), E(n["nota"])) for n in s["numeri"])
    p.append('<h2 id="numeri">Numeri da verificare</h2><p>Valori scritti oggi nei testi o nelle bozze. Molti sono scelte di redazione, senza un dato che li sostenga.</p>'
             '<ul>%s</ul>' % righe)
    p.append('<h2 id="domande">Le domande</h2><ol>%s</ol>' % "".join('<li id="d%d"><p>%s</p></li>' % (i + 1, E(d)) for i, d in enumerate(s["domande"])))
    p.append('<h2 id="leggere">Che cosa leggere</h2><p>Gli articoli a cui si riferiscono le domande. I numeri portano direttamente all\'articolo.</p>%s' % da_leggere(s, sito_dir))
    if s.get("approfondire"):
        p.append('<h2 id="approfondire">Per approfondire</h2><ul>%s</ul>'
                 % "".join('<li><a href="../%s">%s</a></li>' % (E(a["pagina"]), E(a["titolo"])) for a in s["approfondire"]))
    p.append('<h2 id="rispondere">Come rispondere</h2>%s' % rispondere(s))
    return ('<article class="foglio largo"><header class="apertura"><h1>%s</h1></header><div class="prosa">%s</div></article>'
            % (E(s["titolo"]), "\n".join(p)))


MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto",
        "settembre", "ottobre", "novembre", "dicembre"]


def data_it(d):
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})$", d or "")
    return "%d %s %s" % (int(m.group(3)), MESI[int(m.group(2)) - 1], m.group(1)) if m else E(d or "")


def pagina_indice(schede):
    voci = "".join('<li><a href="%s.html"><strong>%s</strong></a><br><span class="piccolo">%s</span></li>'
                   % (s["slug"], E(s["titolo"]), E(s["a_chi"][0].upper() + s["a_chi"][1:])) for s in schede)
    corpo = ('<p class="briciole"><a href="../index.html">Progetto dei Cerchi</a> · Schede per esperti</p>'
             "<p>%s</p>"
             "<p>Ogni scheda è pensata per chi conosce una materia: spiega in poche righe che cosa prevedono le regole, "
             "quali numeri sono incerti e pone circa dodici domande precise, ciascuna con l'articolo a cui si riferisce. "
             "Si può mandare il link di una scheda a chi è competente: si legge senza account e senza conoscere il resto del progetto.</p>"
             '<h2 id="materie">Le materie</h2><ul class="schede-esperti">%s</ul>'
             '<h2 id="altro">Una materia che manca?</h2><p>Se la vostra competenza non è in elenco, il punto di partenza sono i '
             '<a href="../registro/parametri.html">parametri da verificare</a> e il <a href="../registro/index.html">registro delle regole</a>. '
             'Si può scrivere a <a href="mailto:%s">%s</a>.</p>' % (PROGETTO, voci, CONTATTO, CONTATTO))
    return ('<article class="foglio largo"><header class="apertura"><h1>Schede per esperti</h1></header><div class="prosa">%s</div></article>' % corpo)


def costruisci(lingua, pagina, scrivi, radice, sito_dir):
    cartella = os.path.join(radice, "testi", lingua["codice"], "esperti")
    if not os.path.isdir(cartella):
        return
    schede = sorted((json.load(open(f, encoding="utf-8")) for f in glob.glob(os.path.join(cartella, "*.json"))),
                    key=lambda s: s.get("ordine", 99))
    cost = open(os.path.join(radice, "testi", lingua["codice"], lingua["dir_registro"], "costituzione.md"), encoding="utf-8").read()
    versione = (re.search(r'^versione: "(.*)"', cost, re.M) or [None, ""])[1]
    for s in schede:
        scrivi(lingua, "esperti/%s.html" % s["slug"],
               pagina(lingua, "%s — Schede per esperti — %s" % (s["titolo"], lingua["nome"]),
                      "Scheda per %s: le regole del Progetto dei Cerchi da verificare, con domande precise." % s["a_chi"],
                      pagina_scheda(s, sito_dir, versione), 1, "esperti"))
    scrivi(lingua, "esperti/index.html",
           pagina(lingua, "Schede per esperti — %s" % lingua["nome"],
                  "Una scheda per materia, da mandare a chi è competente: che cosa prevedono le regole, i numeri incerti, le domande.",
                  pagina_indice(schede), 1, "esperti"))
