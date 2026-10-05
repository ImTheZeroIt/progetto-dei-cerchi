#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ricerca nei testi e domande frequenti: la parte del sito che risponde alle domande.

Questo modulo è usato da costruisci.py. Fa tre cose:

1. divide ogni testo in unità (un articolo, un comma della Costituzione, una sezione) e ne ricava
   l'indice che la pagina «Trova una risposta» legge nel browser;
2. legge le domande frequenti da un file Markdown (DOMANDE.md, QUESTIONS.md, PREGUNTAS.md) e controlla
   che ogni richiamo a un articolo esista davvero: se un articolo non c'è, la costruzione si ferma;
3. prepara la pagina.

La ricerca avviene tutta nel browser di chi legge (strumenti/cerca.js): nessun servizio esterno,
nessuna domanda inviata o registrata. Non è un'intelligenza artificiale: confronta parole.

Formato del file delle domande:

    ## Nome del gruppo

    ### La domanda?

    La risposta, in uno o più paragrafi.

    Parole: sinonimi, parole che una persona userebbe, separati da virgole
    Dove: Cost. 4.1; Cod. 3, art. 12, c. 1; Annex A, art. 4; All. C, art. 7; [Un'altra pagina](pagina.html)
"""
import html
import json
import re

# Nome del file, nome della pagina e scritte, per lingua.
LINGUE = {
    "it": dict(
        md="DOMANDE.md", pagina="domande.html", voce="Domande",
        sotto="Scrivi una domanda o una parola. Trovi una risposta breve, quando c'è, e gli articoli che ne parlano.",
        etichetta="La tua domanda", segnaposto="lavoro, casa, denaro, uscire…", cerca="Cerca",
        nota="Non è un'intelligenza artificiale: confronta le tue parole con i testi e ti porta all'articolo. "
             "La ricerca avviene nel tuo browser: nessuna domanda viene inviata o registrata.",
        senza_script="Per cercare serve JavaScript. Qui sotto trovi comunque le domande più comuni.",
        frequenti="Domande frequenti", dove="Dove leggerlo",
        h_risposta="Risposta breve", h_testi="Dove se ne parla nei testi",
        carico="Carico i testi…",
        nessuno="Nessun risultato per queste parole. Prova con parole più semplici o con un sinonimo.",
        nessuno_aiuto="Se la risposta manca, <a href=\"{con}\">dillo</a>: è una lacuna da segnalare.",
        risultati="{n} passi trovati. Ecco i più pertinenti.", un_risultato="Un passo trovato.",
        leggi="Leggi nel testo", altri="Mostra altri risultati", tutte="Vedi tutte le domande",
        home_titolo="Hai un'altra domanda?", home_bottone="Trova una risposta",
        descrizione="Domande frequenti sul Progetto dei Cerchi e ricerca negli articoli della Costituzione e dei Codici.",
        comma="comma",
    ),
    "en": dict(
        md="QUESTIONS.md", pagina="questions.html", voce="Questions",
        sotto="Type a question or a word. You get a short answer, when there is one, and the articles that deal with it.",
        etichetta="Your question", segnaposto="work, home, money, leaving…", cerca="Search",
        nota="This is not an artificial intelligence: it compares your words with the texts and takes you to the "
             "article. The search runs in your browser: no question is sent or recorded.",
        senza_script="Searching needs JavaScript. The most common questions are listed below anyway.",
        frequenti="Frequently asked questions", dove="Where to read it",
        h_risposta="Short answer", h_testi="Where the texts deal with it",
        carico="Loading the texts…",
        nessuno="No results for these words. Try simpler words or a synonym.",
        nessuno_aiuto="If the answer is missing, <a href=\"{con}\">say so</a>: it is a gap worth reporting.",
        risultati="{n} passages found. Here are the most relevant.", un_risultato="One passage found.",
        leggi="Read in the text", altri="Show more results", tutte="See all the questions",
        home_titolo="Another question?", home_bottone="Find an answer",
        descrizione="Frequently asked questions about the Circles Project and a search across the articles of the "
                    "Constitution and the Codes.",
        comma="paragraph",
    ),
    "es": dict(
        md="PREGUNTAS.md", pagina="preguntas.html", voce="Preguntas",
        sotto="Escribe una pregunta o una palabra. Encuentras una respuesta breve, cuando la hay, y los pasajes "
              "que hablan de ello.",
        etichetta="Tu pregunta", segnaposto="trabajo, casa, dinero, salir…", cerca="Buscar",
        nota="No es una inteligencia artificial: compara tus palabras con los textos y te lleva al pasaje. "
             "La búsqueda se hace en tu navegador: ninguna pregunta se envía ni se registra. "
             "Las reglas (Constitución y Códigos) están por ahora en italiano e inglés.",
        senza_script="Para buscar hace falta JavaScript. Abajo están de todos modos las preguntas más comunes.",
        frequenti="Preguntas frecuentes", dove="Dónde leerlo",
        h_risposta="Respuesta breve", h_testi="Dónde lo tratan los textos",
        carico="Cargando los textos…",
        nessuno="Ningún resultado para estas palabras. Prueba con palabras más sencillas o con un sinónimo.",
        nessuno_aiuto="Si falta la respuesta, <a href=\"{con}\">dilo</a>: es una laguna que conviene señalar.",
        risultati="{n} pasajes encontrados. Estos son los más pertinentes.", un_risultato="Un pasaje encontrado.",
        leggi="Leer en el texto", altri="Mostrar más resultados", tutte="Ver todas las preguntas",
        home_titolo="¿Tienes otra pregunta?", home_bottone="Encuentra una respuesta",
        descrizione="Preguntas frecuentes sobre el Proyecto de los Círculos y búsqueda en los textos.",
        comma="apartado",
    ),
}

COMMA = re.compile(r"^(\d+\.\d+(?:-[a-z]+)?)\. ", re.M)


# ------------------------------------------------------------------ ancore e testo

def ancore_commi(corpo):
    """Dà un'ancora a ogni comma numerato della Costituzione: «10.3.» diventa raggiungibile come #c-10.3."""
    return re.sub(r"<p>(\d+\.\d+(?:-[a-z]+)?)\. ", r'<p id="c-\1">\1. ', corpo)


def titoli_html(corpo):
    """I titoli di una pagina, nell'ordine: (ancora, testo)."""
    return [(m.group(2) or "", re.sub(r"<[^>]+>", "", html.unescape(m.group(3))).strip())
            for m in re.finditer(r'<h([1-6])(?: id="([^"]*)")?[^>]*>(.*?)</h\1>', corpo, re.S)]


def testo_semplice(markdown):
    """Toglie la sintassi Markdown: resta il testo, una riga per capoverso o voce di elenco."""
    t = re.sub(r"<[^>]+>", " ", markdown)
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", t)
    t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"^\s*\|?[\s:|-]{3,}\|?\s*$", "", t, flags=re.M)        # riga di separazione delle tabelle
    t = t.replace("|", " · ")
    t = re.sub(r"[*_`]+", "", t)
    t = re.sub(r"^\s*>+\s?", "", t, flags=re.M)
    t = re.sub(r"^\s*[-+]\s+", "", t, flags=re.M)
    t = re.sub(r"[ \t]+", " ", t)
    righe = [r.strip(" ·") for r in t.split("\n")]
    return "\n".join(r for r in righe if r)


def unita(markdown, corpo, costituzione=False):
    """Divide un testo in unità di ricerca: [ancora, titolo, numero, testo].

    I titoli del Markdown e quelli della pagina sono nello stesso ordine: da lì viene l'ancora.
    Nella Costituzione ogni comma numerato è un'unità a sé.
    """
    titoli = titoli_html(corpo)
    pezzi = re.split(r"^(#{1,6}) +(.*)$", markdown, flags=re.M)
    sezioni = [("", "", pezzi[0])]
    for i in range(1, len(pezzi), 3):
        sezioni.append((pezzi[i], pezzi[i + 1].strip(), pezzi[i + 2]))
    if len(sezioni) - 1 != len(titoli):
        raise ValueError("i titoli del Markdown (%d) e della pagina (%d) non coincidono"
                         % (len(sezioni) - 1, len(titoli)))
    uscita = []
    for n, (_, titolo, testo) in enumerate(sezioni):
        ancora = titoli[n - 1][0] if n else ""
        titolo = testo_semplice(titolo)
        if costituzione and COMMA.search(testo):
            parti = COMMA.split(testo)
            if parti[0].strip():
                uscita.append([ancora, titolo, "", testo_semplice(parti[0])])
            for i in range(1, len(parti), 2):
                uscita.append(["c-" + parti[i], titolo, parti[i], testo_semplice(parti[i + 1])])
        else:
            pulito = testo_semplice(testo)
            for pezzo in _a_pezzi(pulito):
                uscita.append([ancora, titolo, "", pezzo])
    return uscita


def _a_pezzi(testo, soglia=3000, misura=1500):
    """Un testo molto lungo è diviso in pezzi di qualche capoverso: la ricerca è più precisa."""
    if len(testo) <= soglia:
        return [testo] if testo else []
    pezzi, corrente = [], ""
    for riga in testo.split("\n"):
        if corrente and len(corrente) + len(riga) > misura:
            pezzi.append(corrente)
            corrente = riga
        else:
            corrente = (corrente + "\n" + riga) if corrente else riga
    if corrente:
        pezzi.append(corrente)
    return pezzi


def ancore_articoli(corpo):
    """Per un testo normativo: numero dell'articolo -> ancora, e insieme dei commi con ancora."""
    articoli = {}
    for ancora, _ in titoli_html(corpo):
        m = re.match(r"art-(\d+(?:-[a-z]+)?)--", ancora) or re.match(r"art-(\d+(?:-[a-z]+)?)$", ancora)
        if m:
            articoli.setdefault(m.group(1), ancora)
    commi = set(re.findall(r'<p id="c-([^"]+)">', corpo))
    return articoli, commi


# ------------------------------------------------------------------ domande frequenti

RICHIAMI = [
    (re.compile(r"^(?:Cost|Const)\.\s*(\d+\.\d+(?:-[a-z]+)?)$"), "cost"),
    (re.compile(r"^(?:Cod\.|Code|Cód\.)\s*(\d+),\s*art\.\s*(\d+(?:-[a-z]+)?)(?:,.*)?$"), "codice"),
    (re.compile(r"^Annex A,\s*art\.\s*(\d+(?:-[a-z]+)?)(?:,.*)?$"), "annex"),
    (re.compile(r"^(?:All\.|Annex 16-|Anexo)\s*([ABC]),\s*art\.\s*(\d+(?:-[a-z]+)?)(?:,.*)?$"), "allegato"),
]


def risolvi(richiamo, registro, base):
    """Trasforma «Cod. 3, art. 12, c. 1» in un collegamento. Se l'articolo non esiste, errore.

    registro: identificativo del testo -> dict(slug=…, articoli={numero: ancora}, commi={…}, costituzione=bool)
    base:     indirizzo della cartella delle regole, visto dalla pagina delle domande.
    """
    richiamo = richiamo.strip()
    m = re.match(r"^\[([^\]]+)\]\(([^)]+)\)$", richiamo)
    if m:
        return m.group(1), m.group(2)
    for modello, tipo in RICHIAMI:
        m = modello.match(richiamo)
        if not m:
            continue
        if tipo == "cost":
            testo = next(v for v in registro.values() if v["costituzione"])
            if m.group(1) not in testo["commi"]:
                raise ValueError("il comma %s della Costituzione non esiste" % m.group(1))
            return richiamo, "%s/%s.html#c-%s" % (base, testo["slug"], m.group(1))
        if tipo == "codice":
            chiave, articolo = "codice-%02d" % int(m.group(1)), m.group(2)
        elif tipo == "annex":
            chiave, articolo = "codice-01-annex-a", m.group(1)
        else:
            chiave, articolo = "codice-16-allegato-%s" % m.group(1).lower(), m.group(2)
        if chiave not in registro:
            raise ValueError("il testo «%s» non esiste" % chiave)
        if articolo not in registro[chiave]["articoli"]:
            raise ValueError("l'articolo %s di %s non esiste" % (articolo, chiave))
        return richiamo, "%s/%s.html#%s" % (base, registro[chiave]["slug"], registro[chiave]["articoli"][articolo])
    raise ValueError("richiamo non riconosciuto: «%s»" % richiamo)


def leggi_domande(percorso, registro, base):
    """Legge il file delle domande. Restituisce (titolo, premessa, gruppi).

    gruppi: [(nome, [dict(domanda, ancora, paragrafi, parole, dove=[(testo, indirizzo)])])]
    """
    testo = open(percorso, encoding="utf-8").read()
    titolo = re.match(r"# (.*)\n", testo).group(1).strip()
    corpo = testo.split("\n", 1)[1]
    premessa, *blocchi = re.split(r"^## +(.*)$", corpo, flags=re.M)
    gruppi, viste = [], set()
    for i in range(0, len(blocchi), 2):
        nome, contenuto = blocchi[i].strip(), blocchi[i + 1]
        domande = []
        voci = re.split(r"^### +(.*)$", contenuto, flags=re.M)
        for j in range(1, len(voci), 2):
            domanda, resto = voci[j].strip(), voci[j + 1]
            parole, dove, paragrafi = [], [], []
            for paragrafo in [p.strip() for p in resto.split("\n\n") if p.strip()]:
                righe = []
                for riga in paragrafo.split("\n"):
                    m = re.match(r"^(Parole|Words|Palabras):\s*(.*)$", riga)
                    n = re.match(r"^(Dove|Where|Dónde):\s*(.*)$", riga)
                    if m:
                        parole = [p.strip() for p in m.group(2).split(",") if p.strip()]
                    elif n:
                        for richiamo in [r for r in n.group(2).split(";") if r.strip()]:
                            try:
                                dove.append(risolvi(richiamo, registro, base))
                            except ValueError as errore:
                                raise ValueError("%s, domanda «%s»: %s" % (percorso, domanda, errore))
                    else:
                        righe.append(riga)
                if righe:
                    paragrafi.append(" ".join(righe))
            ancora = "d-" + re.sub(r"[^a-z0-9]+", "-", _senza_accenti(domanda.lower())).strip("-")[:60]
            if ancora in viste:
                raise ValueError("%s: due domande con la stessa ancora «%s»" % (percorso, ancora))
            viste.add(ancora)
            if not paragrafi or not dove:
                raise ValueError("%s, domanda «%s»: manca la risposta o la riga «Dove:»" % (percorso, domanda))
            domande.append(dict(domanda=domanda, ancora=ancora, paragrafi=paragrafi, parole=parole, dove=dove))
        gruppi.append((nome, domande))
    return titolo, premessa.strip(), gruppi


def _senza_accenti(testo):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", testo) if unicodedata.category(c) != "Mn")


def _risposta_html(domanda, etichetta_dove):
    paragrafi = "".join("<p>%s</p>" % html.escape(p) for p in domanda["paragrafi"])
    dove = " · ".join('<a href="%s">%s</a>' % (html.escape(u), html.escape(t)) for t, u in domanda["dove"])
    return '%s<p class="dove"><span>%s:</span> %s</p>' % (paragrafi, etichetta_dove, dove)


# ------------------------------------------------------------------ pagina e indice

def pagina_domande(codice, titolo, premessa, gruppi, base_assets, contribuire):
    """Il corpo della pagina «Trova una risposta»."""
    t = LINGUE[codice]
    elenco = []
    for nome, domande in gruppi:
        elenco.append("<h3>%s</h3>" % html.escape(nome))
        for d in domande:
            elenco.append('<details class="domanda" id="%s"><summary>%s</summary><div class="risposta">%s</div></details>'
                          % (d["ancora"], html.escape(d["domanda"]), _risposta_html(d, t["dove"])))
    return """<section class="foglio cerca">
<header class="apertura">
  <h1>%(titolo)s</h1>
  <p class="sottotitolo">%(sotto)s</p>
</header>
<form id="cerca-form" class="cerca-form" role="search" action="%(pagina)s" method="get">
  <label for="q">%(etichetta)s</label>
  <div class="cerca-riga">
    <input id="q" name="q" type="search" autocomplete="off" spellcheck="false" placeholder="%(segnaposto)s">
    <button class="bottone" type="submit">%(cerca)s</button>
  </div>
  <p class="cerca-nota">%(nota)s</p>
  <noscript><p class="cerca-nota">%(senza_script)s</p></noscript>
</form>
<div id="cerca-esito" class="cerca-esito" aria-live="polite"></div>
<div id="frequenti" class="frequenti">
<h2>%(frequenti)s</h2>
<p class="guida">%(premessa)s</p>
%(elenco)s
</div>
</section>
<script src="%(base)sassets/indice-%(codice)s.js" defer></script>
<script src="%(base)sassets/cerca.js" defer></script>""" % dict(
        titolo=html.escape(titolo), sotto=t["sotto"], pagina=t["pagina"], etichetta=t["etichetta"],
        segnaposto=html.escape(t["segnaposto"]), cerca=t["cerca"], nota=t["nota"], senza_script=t["senza_script"],
        frequenti=t["frequenti"], premessa=html.escape(premessa), elenco="\n".join(elenco), base=base_assets,
        codice=codice)


def modulo_home(codice):
    """Il piccolo modulo di ricerca nella pagina iniziale."""
    t = LINGUE[codice]
    return """<form class="cerca-form cerca-home" role="search" action="%(pagina)s" method="get">
    <label for="q">%(titolo)s</label>
    <div class="cerca-riga">
      <input id="q" name="q" type="search" autocomplete="off" placeholder="%(segnaposto)s">
      <button class="bottone" type="submit">%(bottone)s</button>
    </div>
  </form>""" % dict(pagina=t["pagina"], titolo=t["home_titolo"], segnaposto=html.escape(t["segnaposto"]),
                    bottone=t["home_bottone"])


def indice_js(codice, documenti, gruppi, contribuire):
    """Il file che la pagina carica: testi divisi in unità, domande, scritte.

    documenti: [(titolo, indirizzo, [unità], peso)]. Il peso mette prima le regole in vigore e dopo le bozze.
    """
    t = LINGUE[codice]
    docs, unita_ = [], []
    for n, (titolo, indirizzo, elenco, peso) in enumerate(documenti):
        docs.append([titolo, indirizzo, peso])
        for ancora, titolo_sezione, numero, testo in elenco:
            unita_.append([n, ancora, titolo_sezione, numero, testo])
    domande = []
    for nome, elenco in gruppi:
        for d in elenco:
            domande.append(dict(q=d["domanda"], a=d["ancora"], k=d["parole"], x=" ".join(d["paragrafi"]),
                                h=_risposta_html(d, t["dove"]), r=[u for _, u in d["dove"] if "#" in u]))
    scritte = dict((k, t[k]) for k in ("h_risposta", "h_testi", "carico", "nessuno", "risultati", "un_risultato",
                                       "leggi", "altri", "tutte", "comma"))
    scritte["nessuno_aiuto"] = t["nessuno_aiuto"].format(con=contribuire)
    dati = dict(lingua=codice, t=scritte, docs=docs, unita=unita_, domande=domande)
    return "window.CERCHI_INDICE = %s;\n" % json.dumps(dati, ensure_ascii=False, separators=(",", ":"))
