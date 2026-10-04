#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Costruisce il sito del Progetto dei Cerchi a partire dai testi in Markdown.
Builds the Circles Project website from the Markdown texts.

Uso / usage (dalla cartella principale del repository / from the repository root):

    python3 strumenti/costruisci.py

Legge   testi/it/…  e  testi/en/…
Scrive  docs/  (italiano)  e  docs/en/  (English)

Serve soltanto Python 3 e pandoc (https://pandoc.org). Nessun altro
programma, nessuna libreria esterna, nessun servizio in rete.
"""
import glob
import html
import json
import math
import os
import re
import shutil
import subprocess
import sys

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTI = os.path.join(RADICE, "testi")
SITO_DIR = os.path.join(RADICE, "docs")

# Due licenze: le regole si possono modificare, i quattro testi del percorso no.
LICENZA = "CC BY-SA 4.0"            # Costituzione, Codici, Allegati, sito, strumenti
LICENZA_PERCORSO = "CC BY-ND 4.0"   # i quattro testi del percorso
# Indirizzo pubblico del repository: compilare dopo la pubblicazione.
# Se resta vuoto, i collegamenti al repository non vengono mostrati.
REPOSITORY = "https://github.com/ImTheZeroIt/progetto-dei-cerchi"
# Indirizzo pubblico del sito, senza barra finale (per esempio https://nome.github.io/progetto-dei-cerchi).
# Se compilato, ogni pagina indica l'immagine di anteprima che i social mostrano quando si condivide un link.
SITO_URL = "https://imthezeroit.github.io/progetto-dei-cerchi"

# Ogni lingua ha le proprie cartelle, i propri nomi di pagina e le proprie scritte.
LINGUE = {
    "it": dict(
        codice="it", prefisso="", altra="en", nome_altra="English",
        nome="Progetto dei Cerchi",
        dir_percorso="percorso", dir_registro="registro", dir_scarica="scarica",
        pag_modifiche="modifiche.html", pag_contribuire="contribuire.html",
        md_modifiche="REGISTRO-DELLE-MODIFICHE.md", md_contribuire="CONTRIBUIRE.md",
        licenza_url="https://creativecommons.org/licenses/by-sa/4.0/deed.it",
        licenza_percorso_url="https://creativecommons.org/licenses/by-nd/4.0/deed.it",
        livelli=[("Nucleo di cura", "da 1 a 15 persone", ["cura quotidiana", "e ospitalità"]),
                 ("Comunità di base", "di norma 30–500 persone", ["decide in Assemblea,", "gestisce lavoro e Magazzino"]),
                 ("Bacino", "di norma almeno 3 Comunità", ["logistica, ospedale,", "Tribunale di Garanzia"]),
                 ("Bioregione", "più Bacini", ["ferrovie, energia,", "alta specializzazione"]),
                 ("Cerchio globale", "l’intera umanità", ["regole tecniche comuni,", "nessun governo"])],
        ciclo=[("Bisogni", ["ciò che serve", "alle persone"]),
               ("Assemblea", ["tutte le persone,", "un voto a testa"]),
               ("Lavoro necessario", ["a rotazione; in media", "non oltre 15 ore", "a settimana"]),
               ("Magazzini comuni", ["beni e servizi", "di tutti"]),
               ("Accesso", ["a ciascuno", "secondo il bisogno"])],
        frecce=["rilevati", "decide", "produce", "danno"],
        maiuscole=["Confederazione", "Cerchi", "Codice", "Annex", "Assemblea", "Rete", "Magazzini Comuni",
                   "Contributo di Base Obbligatorio"],
        t=dict(
            salta="Vai al contenuto", sezioni="Sezioni", percorso="Percorso", registro="Registro",
            contribuire="Contribuire", repository="Repository",
            piede="La Costituzione, i Codici e gli Allegati sono pubblicati con licenza {lic}: chiunque può "
                  "copiarli, modificarli e ripubblicarli, citando la fonte e mantenendo la stessa licenza. "
                  "I quattro testi del percorso sono pubblicati con licenza {licp}: si possono copiare e "
                  "ripubblicare per intero, citando la fonte, ma non modificare.",
            piede_registro="Questo testo è pubblicato con licenza {lic}: chiunque può copiarlo, modificarlo e "
                           "ripubblicarlo, citando la fonte e mantenendo la stessa licenza.",
            piede_percorso="Questo testo è pubblicato con licenza {licp}: chiunque può copiarlo e ripubblicarlo "
                           "per intero, citando la fonte, ma non modificarlo. Per tradurlo o adattarlo serve il "
                           "permesso degli autori: vedi <a href=\"{con}\">come contribuire</a>.",
            avviso="",
            modifiche="Registro delle modifiche", come_contribuire="Come contribuire",
            capitolo="Capitolo {n} di {tot} · {min} min di lettura",
            continua="Continua · capitolo {n} di {tot}",
            fine="Il percorso finisce qui", leggi_regole="Leggi le regole",
            fine_testo="La Costituzione, i sedici Codici e gli Allegati, con tutte le versioni.",
            inizio="← Inizio", capitoli="Capitoli", scarica="Scarica", indice="Indice",
            indice_aria="Indice del testo",
            allineamento="Versioni degli altri testi con cui è allineato",
            reg_sotto="Tutti i testi normativi del progetto, con la loro versione. Ogni modifica è annotata e "
                      "motivata nel <a href=\"{mod}\">registro delle modifiche</a>.",
            h_cost="Costituzione", h_codici="Codici", h_allegati="Allegati tecnici",
            h_come="Come sono organizzati",
            come="La Costituzione stabilisce i principi e la struttura generale. I Codici trasformano quei "
                 "principi in regole operative. Gli Allegati tecnici sviluppano procedure, criteri e specifiche. "
                 "In caso di conflitto prevale la Costituzione.",
            desc_reg="Costituzione, Codici e Allegati del Progetto dei Cerchi, con tutte le versioni.",
            versione="versione",
            etichetta="Una proposta aperta", domanda="Quali alternative abbiamo?",
            attacco="Il Progetto dei Cerchi è una proposta di alternativa al modo in cui oggi organizziamo la "
                    "vita collettiva. Comincia dalla persona, organizza la collettività e costruisce gli "
                    "strumenti perché nessuna delle due debba dominare l’altra.",
            comincia="Comincia dal percorso", vai_regole="Vai alle regole",
            h_percorso="Il percorso",
            guida_percorso="Quattro letture in sequenza: da dove veniamo, dove siamo, che cosa non funziona, "
                           "che cosa proponiamo.",
            h_regole="Le regole",
            guida_regole="La proposta è scritta per intero, articolo per articolo, perché possa essere "
                         "verificata e corretta.",
            codici_allegati="{nc} Codici e {na} Allegati tecnici", storico="storico",
            h_aperto="Un progetto aperto", h_stato="Stato", h_licenza="Licenza",
            stato="Il progetto è nella fase di scrittura e verifica. I testi non sono un modello dimostrato: "
                  "devono essere sperimentati, e dove falliscono vanno corretti.",
            licenza="Le regole sono libere: {lic}. Si possono copiare, modificare e ripubblicare, citando la "
                    "fonte e mantenendo la stessa licenza. I quattro testi del percorso si possono copiare e "
                    "ripubblicare per intero, ma non modificare: {licp}.",
            contribuire_testo="Leggere, criticare, verificare, correggere. Servono competenze diverse e casi "
                              "concreti con cui mettere alla prova le regole.",
            desc_home="Una proposta aperta di alternativa al modo in cui organizziamo la vita collettiva: "
                      "il percorso, la Costituzione, i Codici.",
            figura="Persone disposte in cerchio, tutte uguali, con altre comunità collegate attorno",
            si_uniscono="si uniscono in",
            ritorno="nascono nuovi bisogni, e il ciclo ricomincia",
            consigli="Consigli tecnici e IA", consigli2="propongono e calcolano, non decidono",
            garanzia="Cerchio di Garanzia", garanzia2="controlla e riceve i ricorsi; incarichi brevi, a sorteggio",
            did_livelli="I cinque livelli, dalla persona al pianeta. Nessun livello comanda quello sotto: ogni "
                        "decisione resta al livello più vicino che può prenderla.",
            did_ciclo="Come funziona una Comunità: si parte dai bisogni, l’Assemblea decide, il lavoro necessario "
                      "riempie i Magazzini e ciascuno accede secondo il bisogno.",
        ),
    ),
    "en": dict(
        codice="en", prefisso="en/", altra="it", nome_altra="Italiano",
        nome="The Circles Project",
        dir_percorso="path", dir_registro="register", dir_scarica="en/download",
        pag_modifiche="changes.html", pag_contribuire="contributing.html",
        md_modifiche="CHANGELOG.md", md_contribuire="CONTRIBUTING.md",
        licenza_url="https://creativecommons.org/licenses/by-sa/4.0/",
        licenza_percorso_url="https://creativecommons.org/licenses/by-nd/4.0/",
        livelli=[("Care nucleus", "1 to 15 people", ["daily care", "and hospitality"]),
                 ("Base community", "usually 30–500 people", ["decides in Assembly,", "manages work and Storehouse"]),
                 ("Basin", "usually at least 3 Communities", ["logistics, hospital,", "Guarantee Tribunal"]),
                 ("Bioregion", "several Basins", ["railways, energy,", "high specialisation"]),
                 ("Global circle", "the whole of humanity", ["common technical rules,", "no government"])],
        ciclo=[("Needs", ["what people", "need"]),
               ("Assembly", ["everyone,", "one vote each"]),
               ("Necessary work", ["in rotation; on average", "no more than 15 hours", "a week"]),
               ("Storehouses", ["goods and services", "belonging to all"]),
               ("Access", ["to each", "according to need"])],
        frecce=["surveyed", "decides", "produces", "give"],
        maiuscole=["Confederation", "Circles", "Code", "Annex", "Assembly", "Network", "Common Storehouses",
                   "Mandatory Base Contribution", "Technical"],
        t=dict(
            salta="Skip to content", sezioni="Sections", percorso="Path", registro="Register",
            contribuire="Contributing", repository="Repository",
            piede="The Constitution, the Codes and the Annexes are published under the {lic} licence: anyone "
                  "may copy, modify and republish them, citing the source and keeping the same licence. "
                  "The four texts of the path are published under the {licp} licence: they may be copied and "
                  "republished in full, citing the source, but not modified.",
            piede_registro="This text is published under the {lic} licence: anyone may copy, modify and "
                           "republish it, citing the source and keeping the same licence.",
            piede_percorso="This text is published under the {licp} licence: anyone may copy and republish it "
                           "in full, citing the source, but may not modify it. Translating or adapting it "
                           "requires the authors’ permission: see <a href=\"{con}\">how to contribute</a>.",
            avviso="This is a working translation. The Italian text is the authoritative one.",
            modifiche="Change log", come_contribuire="How to contribute",
            capitolo="Chapter {n} of {tot} · {min} min read",
            continua="Continue · chapter {n} of {tot}",
            fine="The path ends here", leggi_regole="Read the rules",
            fine_testo="The Constitution, the sixteen Codes and the Annexes, with all their versions.",
            inizio="← Start", capitoli="Chapters", scarica="Download", indice="Contents",
            indice_aria="Table of contents",
            allineamento="Versions of the other texts it is aligned with",
            reg_sotto="All the normative texts of the project, with their version. Every change is recorded "
                      "and explained in the <a href=\"{mod}\">change log</a>.",
            h_cost="Constitution", h_codici="Codes", h_allegati="Technical Annexes",
            h_come="How they are organised",
            come="The Constitution sets out the principles and the general structure. The Codes turn those "
                 "principles into operating rules. The Technical Annexes develop procedures, criteria and "
                 "specifications. In case of conflict, the Constitution prevails.",
            desc_reg="Constitution, Codes and Annexes of the Circles Project, with all their versions.",
            versione="version",
            etichetta="An open proposal", domanda="What alternatives do we have?",
            attacco="The Circles Project is a proposal for an alternative to the way we organise collective "
                    "life today. It starts from the person, organises the collectivity and builds the tools "
                    "so that neither has to dominate the other.",
            comincia="Start with the path", vai_regole="Go to the rules",
            h_percorso="The path",
            guida_percorso="Four readings in sequence: where we come from, where we are, what does not work, "
                           "what we propose.",
            h_regole="The rules",
            guida_regole="The proposal is written out in full, article by article, so that it can be "
                         "verified and corrected.",
            codici_allegati="{nc} Codes and {na} Technical Annexes", storico="history",
            h_aperto="An open project", h_stato="Status", h_licenza="Licence",
            stato="The project is at the stage of writing and verification. The texts are not a proven "
                  "model: they must be tested, and corrected where they fail.",
            licenza="The rules are free: {lic}. They may be copied, modified and republished, citing the "
                    "source and keeping the same licence. The four texts of the path may be copied and "
                    "republished in full, but not modified: {licp}.",
            contribuire_testo="Read, criticise, verify, correct. Different skills are needed, and concrete "
                              "cases with which to put the rules to the test.",
            desc_home="An open proposal for an alternative to the way we organise collective life: "
                      "the path, the Constitution, the Codes.",
            figura="People standing in a circle, all equal, with other communities linked around them",
            si_uniscono="join into",
            ritorno="new needs arise, and the cycle starts again",
            consigli="Technical Councils and AI", consigli2="propose and calculate, do not decide",
            garanzia="Guarantee Circle", garanzia2="oversees and hears appeals; short offices, by lot",
            did_livelli="The five levels, from the person to the planet. No level commands the one below: "
                        "every decision stays at the closest level that can take it.",
            did_ciclo="How a Community works: it starts from needs, the Assembly decides, the necessary work "
                      "fills the Storehouses and everyone has access according to need.",
        ),
    ),
}


# ----------------------------------------------------------------- lettura

def leggi(percorso):
    """Restituisce (metadati, corpo) di un file Markdown con intestazione."""
    testo = open(percorso, encoding="utf-8").read()
    m = re.match(r"---\n(.*?)\n---\n", testo, re.S)
    meta = {}
    for riga in m.group(1).split("\n"):
        chiave, valore = riga.split(": ", 1)
        meta[chiave] = json.loads(valore)
    return meta, testo[m.end():].strip("\n")


def pandoc(markdown, indice=False, etichetta="Indice"):
    """Converte Markdown in HTML. Con indice=True restituisce (indice, corpo)."""
    modello = os.path.join(RADICE, "strumenti", "modello-pandoc.html")
    comando = ["pandoc", "-f", "gfm", "-t", "html5", "--wrap=none", "--template", modello]
    if indice:
        comando += ["--toc", "--toc-depth=3"]
    uscita = subprocess.run(comando, input=markdown, capture_output=True, text=True, check=True).stdout
    sommario, corpo = uscita.split("<!--CORPO-->", 1)
    sommario = sommario.replace('aria-label="Indice del testo"', 'aria-label="%s"' % etichetta)
    # le tabelle larghe scorrono dentro il proprio riquadro, non con la pagina
    corpo = corpo.replace("<table>", '<div class="tabella"><table>').replace("</table>", "</table></div>")
    return sommario.strip(), corpo.strip()


def abbassa_titoli(markdown):
    """Il titolo della pagina è h1: nel corpo i titoli partono da h2."""
    if re.search(r"^# ", markdown, re.M):
        return re.sub(r"^(#+) ", lambda m: "#" + m.group(1) + " ", markdown, flags=re.M)
    return markdown


def minuti(markdown):
    return max(1, round(len(markdown.split()) / 200))


def titolo_leggibile(titolo, maiuscole):
    """«CODICE 3 — DELLA DELIBERAZIONE…» → «Codice 3 — Della deliberazione…»."""
    if titolo != titolo.upper():
        return titolo
    parti = []
    for parte in titolo.split(" — "):
        parte = parte.lower()
        parti.append(parte[0].upper() + parte[1:])
    testo = " — ".join(parti)
    for parola in maiuscole:
        testo = re.sub(r"\b%s\b" % re.escape(parola.lower()), parola, testo)
    testo = re.sub(r"\b(Allegato tecnico|Technical annex) ([abc])\b",
                   lambda m: m.group(1) + " " + m.group(2).upper(), testo, flags=re.I)
    testo = re.sub(r"c\.1-annex a", "C.1-Annex A", testo, flags=re.I)
    return testo[0].upper() + testo[1:]


# ----------------------------------------------------------------- pezzi di pagina

def anelli(pieni=0, totale=4, classe="anelli"):
    """Cerchi concentrici: i primi `pieni` (dal centro) sono evidenziati."""
    parti = []
    for i in range(totale):
        stato = "pieno" if i < pieni else "vuoto"
        parti.append('<circle cx="32" cy="32" r="%d" class="%s"/>' % (6 + i * 6, stato))
    return ('<svg class="%s" viewBox="0 0 64 64" width="64" height="64" aria-hidden="true" '
            'focusable="false">%s</svg>') % (classe, "".join(parti))


def simbolo(classe="logo"):
    """Il simbolo del progetto: sette anelli uguali in catena chiusa, uno evidenziato."""
    parti = []
    for i in range(7):
        a = -math.pi / 2 + 2 * math.pi * i / 7
        parti.append('<circle cx="%.2f" cy="%.2f" r="10.4" class="%s"/>'
                     % (32 + 18.2 * math.cos(a), 32 + 18.2 * math.sin(a), "uno" if i == 0 else "an"))
    return ('<svg class="%s" viewBox="0 0 64 64" width="64" height="64" aria-hidden="true" focusable="false">%s</svg>'
            % (classe, "".join(parti)))


def icona():
    """L'icona della scheda del browser, come file SVG a sé."""
    parti = []
    for i in range(7):
        a = -math.pi / 2 + 2 * math.pi * i / 7
        parti.append('<circle cx="%.2f" cy="%.2f" r="9.6" fill="none" stroke="%s" stroke-width="3.6"/>'
                     % (32 + 16.8 * math.cos(a), 32 + 16.8 * math.sin(a), "#e3b24a" if i == 0 else "#f3f5f1"))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" '
            'fill="#0e6656"/>%s</svg>' % "".join(parti))


def copertina(lingua):
    """La copertina: una comunità in cerchio, senza nessuno al centro, e altre comunità collegate."""
    cx, cy, r = 400, 350, 222
    parti = []
    satelliti = [(735, 70, 100, 24, 0.3), (770, 590, 122, 28, 0.9), (430, 760, 88, 22, 0.1),
                 (95, 660, 60, 16, 0.5), (120, 60, 68, 18, 0.7), (520, -75, 66, 18, 0.2)]
    for sx, sy, sr, n, rot in satelliti:
        d = math.hypot(sx - cx, sy - cy)
        ux, uy = (sx - cx) / d, (sy - cy) / d
        parti.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="cp-filo"/>'
                     % (cx + ux * (r + 20), cy + uy * (r + 20), sx - ux * (sr + 13), sy - uy * (sr + 13)))
        for i in range(n):
            a = rot + 2 * math.pi * i / n
            parti.append('<circle cx="%.1f" cy="%.1f" r="4" class="cp-altri"/>'
                         % (sx + sr * math.cos(a), sy + sr * math.sin(a)))
    n = 60
    for i in range(n):
        a = -math.pi / 2 + 2 * math.pi * i / n
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        if i == 8:
            parti.append('<circle cx="%.1f" cy="%.1f" r="11.5" class="cp-io"/>' % (x, y))
        else:
            parti.append('<circle cx="%.1f" cy="%.1f" r="8" class="cp-noi"/>' % (x, y))
    return ('<figure class="copertina"><svg viewBox="0 0 800 700" role="img" aria-label="%s">%s</svg></figure>'
            % (lingua["t"]["figura"], "".join(parti)))


def _testo(x, y, s, classe="", ancora="middle"):
    return '<text x="%s" y="%s" text-anchor="%s"%s>%s</text>' % (
        x, y, ancora, (' class="%s"' % classe) if classe else "", html.escape(s))


def _punta(ident):
    return ('<defs><marker id="%s" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" '
            'orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="punta"/></marker></defs>' % ident)


def figura_livelli(lingua):
    """Schema, prima parte: i cinque livelli affiancati, dalla persona al pianeta."""
    t = lingua["t"]
    ident = "p-livelli-%s" % lingua["codice"]
    xs, raggi, base = [95, 285, 475, 680, 905], [10, 22, 36, 52, 70], 160
    parti = [_punta(ident)]
    for i, (nome, chi, cosa) in enumerate(lingua["livelli"]):
        x, r = xs[i], raggi[i]
        parti.append('<circle cx="%d" cy="%d" r="%d" class="%s"/>' % (x, base - r, r, "liv0" if i == 0 else "liv"))
        parti.append(_testo(x, base - r + (4 if r < 20 else 6), str(i), "num0" if i == 0 else "num"))
        parti.append(_testo(x, base + 30, nome, "nome"))
        parti.append(_testo(x, base + 51, chi, "chi piccolo"))
        for k, riga in enumerate(cosa):
            parti.append(_testo(x, base + 75 + k * 18, riga))
        if i < 4:
            x1, x2 = x + r + 12, xs[i + 1] - raggi[i + 1] - 12
            parti.append('<line x1="%d" y1="%d" x2="%d" y2="%d" class="filo" marker-end="url(#%s)"/>'
                         % (x1, base - 10, x2, base - 10, ident))
            parti.append(_testo((x1 + x2) / 2, base - 19, t["si_uniscono"], "chi piccolo"))
    return ('<figure class="schema"><div class="scorre"><svg viewBox="0 0 1000 262" role="img" aria-label="%s">%s</svg></div>'
            '<figcaption>%s</figcaption></figure>' % (html.escape(t["did_livelli"]), "".join(parti), t["did_livelli"]))


def figura_ciclo(lingua):
    """Schema, seconda parte: dal bisogno al compito, e ritorno."""
    t = lingua["t"]
    ident = "p-ciclo-%s" % lingua["codice"]
    lb, hb, yb = 168, 98, 92
    xs = [0, 208, 416, 624, 832]
    parti = [_punta(ident)]
    for i, (nome, righe) in enumerate(lingua["ciclo"]):
        x = xs[i]
        parti.append('<rect x="%d" y="%d" width="%d" height="%d" rx="9" class="%s"/>'
                     % (x + 1, yb, lb - 2, hb, "nodo scelto" if i == 1 else "nodo"))
        alto = yb + (30 if len(righe) > 2 else 37)
        parti.append(_testo(x + lb / 2, alto, nome, "nome medio"))
        for k, riga in enumerate(righe):
            parti.append(_testo(x + lb / 2, alto + 21 + k * 16, riga, "chi piccolo"))
        if i < 4:
            x1, x2 = x + lb + 4, xs[i + 1] - 4
            parti.append('<line x1="%d" y1="%d" x2="%d" y2="%d" class="filo" marker-end="url(#%s)"/>'
                         % (x1, yb + hb / 2, x2, yb + hb / 2, ident))
            parti.append(_testo((x1 + x2) / 2, yb - 9, lingua["frecce"][i], "chi minimo"))
    # il ritorno: dall'accesso ai bisogni
    yr = yb + hb + 44
    parti.append('<polyline points="%d,%d %d,%d %d,%d %d,%d" class="filo" marker-end="url(#%s)"/>'
                 % (xs[4] + lb / 2, yb + hb + 5, xs[4] + lb / 2, yr, xs[0] + lb / 2, yr, xs[0] + lb / 2, yb + hb + 8, ident))
    parti.append(_testo(500, yr - 9, t["ritorno"], "chi piccolo"))
    # chi aiuta e chi controlla l'Assemblea
    ax = xs[1] + lb / 2
    parti.append('<line x1="%d" y1="50" x2="%d" y2="%d" class="filo tratto" marker-end="url(#%s)"/>' % (ax - 60, ax - 20, yb - 6, ident))
    parti.append(_testo(2, 20, t["consigli"], "nome piccolo", "start"))
    parti.append(_testo(2, 38, t["consigli2"], "chi piccolo", "start"))
    parti.append('<line x1="%d" y1="50" x2="%d" y2="%d" class="filo tratto" marker-end="url(#%s)"/>' % (ax + 60, ax + 20, yb - 6, ident))
    parti.append(_testo(ax + 66, 20, t["garanzia"], "nome piccolo", "start"))
    parti.append(_testo(ax + 66, 38, t["garanzia2"], "chi piccolo", "start"))
    return ('<figure class="schema"><div class="scorre"><svg viewBox="0 0 1000 262" role="img" aria-label="%s">%s</svg></div>'
            '<figcaption>%s</figcaption></figure>' % (html.escape(t["did_ciclo"]), "".join(parti), t["did_ciclo"]))


FIGURE = {"livelli": figura_livelli, "ciclo": figura_ciclo}


def inserisci_figure(corpo, lingua):
    """Sostituisce i segnaposto <!-- figura: nome --> del testo con il disegno corrispondente."""
    return re.sub(r"<!--\s*figura:\s*(\w+)\s*-->", lambda m: FIGURE[m.group(1)](lingua), corpo)


def pagina(lingua, titolo, descrizione, corpo, profondita, sezione="", gemella=""):
    """Avvolge il corpo nella pagina completa.

    profondita: quante cartelle separano la pagina dalla radice della lingua (0 o 1).
    gemella:    indirizzo, relativo alla radice del sito, della stessa pagina nell'altra lingua.
    """
    t = lingua["t"]
    radice = "../" * profondita                                   # radice della lingua
    base = radice + ("../" * lingua["prefisso"].count("/"))       # radice del sito

    def voce(nome, indirizzo, chiave):
        attuale = ' aria-current="page"' if chiave == sezione else ""
        return '<a href="%s%s"%s>%s</a>' % (radice, indirizzo, attuale, nome)

    cambio = ('<a class="lingua" href="%s%s" lang="%s" hreflang="%s">%s</a>'
              % (base, gemella, lingua["altra"], lingua["altra"], lingua["nome_altra"])) if gemella else ""
    deposito = (' · <a href="%s">%s</a>' % (html.escape(REPOSITORY), t["repository"])) if REPOSITORY else ""
    avviso = ('<p class="avviso">%s</p>' % t["avviso"]) if t["avviso"] else ""
    licenza = '<a href="%s">%s</a>' % (lingua["licenza_url"], LICENZA)
    licenza_p = '<a href="%s">%s</a>' % (lingua["licenza_percorso_url"], LICENZA_PERCORSO)
    piede = t["piede_%s" % sezione] if ("piede_%s" % sezione) in t else t["piede"]
    piede = piede.format(lic=licenza, licp=licenza_p, con=radice + lingua["pag_contribuire"])
    return """<!doctype html>
<html lang="%(codice)s">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(titolo)s</title>
<meta name="description" content="%(descrizione)s">
<link rel="stylesheet" href="%(base)sassets/stile.css">
<link rel="icon" href="%(base)sassets/icona.svg" type="image/svg+xml">%(anteprima)s
</head>
<body>
<a class="salta" href="#contenuto">%(salta)s</a>
<header class="testata">
  <a class="marchio" href="%(radice)sindex.html">%(logo)s<span>%(nome)s</span></a>
  <nav aria-label="%(sezioni)s">%(v1)s%(v2)s%(v3)s%(cambio)s</nav>
</header>
<main id="contenuto">
%(corpo)s
</main>
<footer class="piede">
  %(avviso)s
  <p>%(piede)s</p>
  <p class="piccolo"><a href="%(radice)s%(reg)s/%(pmod)s">%(modifiche)s</a> · <a href="%(radice)s%(pcon)s">%(come)s</a>%(deposito)s</p>
</footer>
</body>
</html>
""" % dict(codice=lingua["codice"], titolo=html.escape(titolo), descrizione=html.escape(descrizione),
           base=base, radice=radice, logo=simbolo(), nome=lingua["nome"], corpo=corpo,
           anteprima=('\n<meta property="og:title" content="%s">\n<meta property="og:description" content="%s">'
                      '\n<meta property="og:image" content="%s/assets/copertina.png">'
                      '\n<meta name="twitter:card" content="summary_large_image">'
                      % (html.escape(titolo), html.escape(descrizione), SITO_URL)) if SITO_URL else "",
           salta=t["salta"], sezioni=t["sezioni"], cambio=cambio, avviso=avviso,
           piede=piede, reg=lingua["dir_registro"], pmod=lingua["pag_modifiche"],
           pcon=lingua["pag_contribuire"], modifiche=t["modifiche"], come=t["come_contribuire"],
           deposito=deposito,
           v1=voce(t["percorso"], "index.html#percorso", "percorso"),
           v2=voce(t["registro"], lingua["dir_registro"] + "/index.html", "registro"),
           v3=voce(t["contribuire"], lingua["pag_contribuire"], "contribuire"))


def scrivi(lingua, relativo, contenuto):
    destinazione = os.path.join(SITO_DIR, lingua["prefisso"], relativo)
    os.makedirs(os.path.dirname(destinazione), exist_ok=True)
    open(destinazione, "w", encoding="utf-8").write(contenuto)


def scaricabili(lingua, slug, profondita):
    """Collegamenti ai file da scaricare, se esistono in docs/<dir_scarica>/."""
    base = "../" * profondita + "../" * lingua["prefisso"].count("/")
    voci = []
    for estensione in ("pdf", "odt", "docx"):
        if os.path.exists(os.path.join(SITO_DIR, lingua["dir_scarica"], "%s.%s" % (slug, estensione))):
            voci.append('<a href="%s%s/%s.%s" download>%s</a>'
                        % (base, lingua["dir_scarica"], slug, estensione, estensione.upper()))
    return ('<span class="scarica">%s: %s</span>' % (lingua["t"]["scarica"], " · ".join(voci))) if voci else ""


# ----------------------------------------------------------------- costruzione

def carica(lingua):
    cartella = os.path.join(TESTI, lingua["codice"])
    percorso = sorted((leggi(f) for f in glob.glob(os.path.join(cartella, lingua["dir_percorso"], "*.md"))),
                      key=lambda x: x[0]["capitolo"])
    registro = sorted((leggi(f) for f in glob.glob(os.path.join(cartella, lingua["dir_registro"], "*.md"))),
                      key=lambda x: x[0]["ordine"])
    return percorso, registro


def costruisci_lingua(lingua, altra):
    """Costruisce tutte le pagine di una lingua. `altra` serve per i collegamenti tra le due versioni."""
    t = lingua["t"]
    nome = lingua["nome"]
    percorso, registro = carica(lingua)
    # indirizzi delle pagine gemelle nell'altra lingua, per identificativo comune
    gemelle = {}
    if altra:
        p2, r2 = carica(altra)
        for meta, _ in p2:
            gemelle[meta["id"]] = "%s%s/%s.html" % (altra["prefisso"], altra["dir_percorso"], meta["slug"])
        for meta, _ in r2:
            gemelle[meta["id"]] = "%s%s/%s.html" % (altra["prefisso"], altra["dir_registro"], meta["slug"])
    def gemella(chiave, predefinita=""):
        if not altra:
            return ""
        return gemelle.get(chiave, predefinita)
    costituzione = next(m for m, _ in registro if m["gruppo"] == "costituzione")
    dp, dr = lingua["dir_percorso"], lingua["dir_registro"]

    # --- capitoli del percorso
    for i, (meta, testo) in enumerate(percorso):
        _, corpo = pandoc(testo)
        corpo = inserisci_figure(corpo, lingua)
        n, tot = meta["capitolo"], len(percorso)
        if i + 1 < tot:
            dopo = percorso[i + 1][0]
            seguito = ('<a class="seguito" href="%s.html"><span class="etichetta">%s</span><strong>%s</strong>'
                       '<span>%s</span></a>' % (dopo["slug"], t["continua"].format(n=dopo["capitolo"], tot=tot),
                                                dopo["titolo"], dopo["sintesi"]))
        else:
            seguito = ('<a class="seguito" href="../%s/index.html"><span class="etichetta">%s</span>'
                       '<strong>%s</strong><span>%s</span></a>' % (dr, t["fine"], t["leggi_regole"], t["fine_testo"]))
        prima = ('<a href="%s.html">← %s</a>' % (percorso[i - 1][0]["slug"], percorso[i - 1][0]["titolo"])) if i \
            else '<a href="../index.html">%s</a>' % t["inizio"]
        contenuto = """<article class="lettura">
<header class="apertura">
  <p class="passo">%(anelli)s<span>%(capitolo)s</span></p>
  <h1>%(titolo)s</h1>
  <p class="sottotitolo">%(sotto)s</p>
</header>
<div class="prosa">
%(corpo)s
</div>
<nav class="avanti" aria-label="%(capitoli)s">
  %(seguito)s
  <p class="indietro">%(prima)s %(scarica)s</p>
</nav>
</article>""" % dict(anelli=anelli(n, tot), capitolo=t["capitolo"].format(n=n, tot=tot, min=minuti(testo)),
                     titolo=meta["titolo"], sotto=meta["sottotitolo"], corpo=corpo, capitoli=t["capitoli"],
                     seguito=seguito, prima=prima, scarica=scaricabili(lingua, meta["slug"], 1))
        scrivi(lingua, "%s/%s.html" % (dp, meta["slug"]),
               pagina(lingua, "%s — %s" % (meta["titolo"], nome), meta["sintesi"], contenuto, 1, "percorso",
                      gemella(meta["id"])))

    # --- testi del registro
    for meta, testo in registro:
        sommario, corpo = pandoc(abbassa_titoli(testo), indice=True, etichetta=t["indice_aria"])
        dettagli = ""
        if meta.get("allineamento"):
            dettagli = ('<details class="allineamento"><summary>%s</summary><p>%s</p></details>'
                        % (t["allineamento"], html.escape(meta["allineamento"])))
        contenuto = """<article class="norma">
<header class="apertura">
  <p class="briciole"><a href="index.html">%(registro)s</a> / %(breve)s</p>
  <h1>%(titolo)s</h1>
  <p class="dati"><span class="versione">%(versione)s</span>%(scarica)s</p>
  %(dettagli)s
</header>
<div class="colonne">
<aside class="indice">
<details id="indice"><summary>%(indice)s</summary>
%(sommario)s
</details>
</aside>
<script>if (window.matchMedia("(min-width: 60rem)").matches) document.getElementById("indice").open = true;</script>
<div class="prosa testo-norma">
%(corpo)s
</div>
</div>
</article>""" % dict(registro=t["registro"], breve=html.escape(meta["breve"]), indice=t["indice"],
                     titolo=html.escape(titolo_leggibile(meta["titolo"], lingua["maiuscole"])),
                     versione=meta["versione"], scarica=scaricabili(lingua, meta["slug"], 1),
                     dettagli=dettagli, sommario=sommario, corpo=corpo)
        scrivi(lingua, "%s/%s.html" % (dr, meta["slug"]),
               pagina(lingua, "%s — %s" % (meta["breve"], nome),
                      "%s, %s %s." % (meta["breve"], t["versione"], meta["versione"]),
                      contenuto, 1, "registro", gemella(meta["id"])))

    # --- indice del registro
    def elenco(gruppo):
        return "\n".join('<li><a href="%s.html">%s</a><span class="versione">%s</span></li>'
                         % (m["slug"], html.escape(m["breve"]), m["versione"])
                         for m, _ in registro if m["gruppo"] == gruppo)
    contenuto = """<section class="foglio">
<header class="apertura">
  <h1>%s</h1>
  <p class="sottotitolo">%s</p>
</header>
<h2>%s</h2>
<ul class="testi">%s</ul>
<h2>%s</h2>
<ul class="testi">%s</ul>
<h2>%s</h2>
<ul class="testi">%s</ul>
<h2>%s</h2>
<p>%s</p>
</section>""" % (t["registro"], t["reg_sotto"].format(mod=lingua["pag_modifiche"]), t["h_cost"],
                 elenco("costituzione"), t["h_codici"], elenco("codici"), t["h_allegati"], elenco("allegati"),
                 t["h_come"], t["come"])
    scrivi(lingua, "%s/index.html" % dr,
           pagina(lingua, "%s — %s" % (t["registro"], nome), t["desc_reg"], contenuto, 1, "registro",
                  gemella("", "%s%s/index.html" % (altra["prefisso"], altra["dir_registro"]) if altra else "")))

    # --- pagine di servizio: modifiche, contribuire
    servizio = (
        (lingua["md_modifiche"], "%s/%s" % (dr, lingua["pag_modifiche"]), t["modifiche"], 1, "registro",
         "%s%s/%s" % (altra["prefisso"], altra["dir_registro"], altra["pag_modifiche"]) if altra else ""),
        (lingua["md_contribuire"], lingua["pag_contribuire"], t["come_contribuire"], 0, "contribuire",
         "%s%s" % (altra["prefisso"], altra["pag_contribuire"]) if altra else ""),
    )
    for origine, destinazione, titolo, profondita, sezione, gem in servizio:
        testo = open(os.path.join(RADICE, origine), encoding="utf-8").read()
        testo = re.sub(r"\A# .*\n", "", testo)
        _, corpo = pandoc(abbassa_titoli(testo))
        contenuto = ('<article class="foglio"><header class="apertura"><h1>%s</h1></header>'
                     '<div class="prosa">%s</div></article>' % (titolo, corpo))
        scrivi(lingua, destinazione,
               pagina(lingua, "%s — %s" % (titolo, nome), titolo + ".", contenuto, profondita, sezione, gem))

    # --- pagina iniziale
    passi = "\n".join(
        '<li><a href="%s/%s.html"><span class="num">%d</span><span class="voce"><strong>%s</strong>'
        '<span>%s</span></span><span class="durata">%d min</span></a></li>'
        % (dp, m["slug"], m["capitolo"], m["titolo"], m["sintesi"], minuti(x)) for m, x in percorso)
    nc = sum(1 for m, _ in registro if m["gruppo"] == "codici")
    na = sum(1 for m, _ in registro if m["gruppo"] == "allegati")
    licenza = '<a href="%s">%s</a>' % (lingua["licenza_url"], LICENZA)
    licenza_p = '<a href="%s">%s</a>' % (lingua["licenza_percorso_url"], LICENZA_PERCORSO)
    contenuto = """<section class="eroe">
  <div>
    <p class="etichetta">%(etichetta)s</p>
    <h1>%(domanda)s</h1>
    <p class="attacco">%(attacco)s</p>
    <p class="azioni"><a class="bottone" href="%(dp)s/%(primo)s.html">%(comincia)s</a><a class="secondario" href="%(dr)s/index.html">%(vai)s</a></p>
  </div>
  %(figura)s
</section>

<section id="percorso" class="blocco">
  <h2>%(h_percorso)s</h2>
  <p class="guida">%(guida_percorso)s</p>
  <ol class="passi">
%(passi)s
  </ol>
</section>

<section class="blocco">
  <h2>%(h_regole)s</h2>
  <p class="guida">%(guida_regole)s</p>
  <ul class="testi">
    <li><a href="%(dr)s/%(cost)s.html">%(h_cost)s</a><span class="versione">%(vcost)s</span></li>
    <li><a href="%(dr)s/index.html">%(codall)s</a><span class="versione">%(registro)s</span></li>
    <li><a href="%(dr)s/%(pmod)s">%(modifiche)s</a><span class="versione">%(storico)s</span></li>
  </ul>
</section>

<section class="blocco">
  <h2>%(h_aperto)s</h2>
  <div class="tre">
    <div><h3>%(h_stato)s</h3><p>%(stato)s</p></div>
    <div><h3>%(h_licenza)s</h3><p>%(licenza)s</p></div>
    <div><h3>%(contribuire)s</h3><p>%(ctesto)s <a href="%(pcon)s">%(come)s</a>.</p></div>
  </div>
</section>""" % dict(
        etichetta=t["etichetta"], domanda=t["domanda"], attacco=t["attacco"], dp=dp, dr=dr,
        primo=percorso[0][0]["slug"], comincia=t["comincia"], vai=t["vai_regole"], figura=copertina(lingua),
        h_percorso=t["h_percorso"], guida_percorso=t["guida_percorso"], passi=passi, h_regole=t["h_regole"],
        guida_regole=t["guida_regole"], cost=costituzione["slug"], h_cost=t["h_cost"],
        vcost=costituzione["versione"], codall=t["codici_allegati"].format(nc=nc, na=na),
        registro=t["registro"].lower(), pmod=lingua["pag_modifiche"], modifiche=t["modifiche"],
        storico=t["storico"], h_aperto=t["h_aperto"], h_stato=t["h_stato"], stato=t["stato"],
        h_licenza=t["h_licenza"], licenza=t["licenza"].format(lic=licenza, licp=licenza_p), contribuire=t["contribuire"],
        ctesto=t["contribuire_testo"], pcon=lingua["pag_contribuire"], come=t["come_contribuire"])
    scrivi(lingua, "index.html",
           pagina(lingua, nome, t["desc_home"], contenuto, 0, "",
                  gemella("", "%sindex.html" % altra["prefisso"] if altra else "")))


def costruisci():
    presenti = [c for c in LINGUE if os.path.isdir(os.path.join(TESTI, c))]
    for codice in presenti:
        lingua = LINGUE[codice]
        altra = LINGUE[lingua["altra"]] if lingua["altra"] in presenti else None
        costruisci_lingua(lingua, altra)
    # foglio di stile e file che evita l'elaborazione Jekyll su alcuni servizi
    os.makedirs(os.path.join(SITO_DIR, "assets"), exist_ok=True)
    shutil.copy(os.path.join(RADICE, "strumenti", "stile.css"), os.path.join(SITO_DIR, "assets", "stile.css"))
    open(os.path.join(SITO_DIR, "assets", "icona.svg"), "w", encoding="utf-8").write(icona())
    anteprima = os.path.join(RADICE, "immagini", "copertina.png")
    if os.path.exists(anteprima):
        shutil.copy(anteprima, os.path.join(SITO_DIR, "assets", "copertina.png"))
    open(os.path.join(SITO_DIR, ".nojekyll"), "w").close()
    print("Sito costruito in", SITO_DIR, "— lingue:", ", ".join(presenti))


if __name__ == "__main__":
    if shutil.which("pandoc") is None:
        sys.exit("Serve pandoc: https://pandoc.org/installing.html")
    costruisci()
