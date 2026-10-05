#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Costruisce il sito del Progetto dei Cerchi a partire dai testi in Markdown.
Builds the Circles Project website from the Markdown texts.

Uso / usage (dalla cartella principale del repository / from the repository root):

    python3 strumenti/costruisci.py

Legge   testi/it/…,  testi/en/…  e  testi/es/…
Scrive  docs/  (italiano),  docs/en/  (English)  e  docs/es/  (español)

Una lingua può avere solo i testi del percorso: in quel caso le sue pagine rimandano
alle regole della lingua indicata in «regole_da».

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

# Indirizzo a cui scrivere per chi non ha un account sul repository.
CONTATTO = "zerocirclesproject@gmail.com"

# Parole con cui cominciano i titoli delle segnalazioni aperte, per tipo: servono ai tre inviti della pagina iniziale.
SEGNALAZIONI = {"caso": "Caso di prova", "dato": "Parametro da confermare", "codice": "Verifica di competenza"}


# Il registro dei parametri da verificare esiste, per ora, solo in italiano.
PARAMETRI = dict(lingua="it", md="PARAMETRI.md", pagina="parametri.html")

# Bozze di calibrazione: allegati tecnici che i Codici citano e che non sono ancora adottati. Per ora solo in italiano.
BOZZE = [
    dict(md="bozze/allegato-paniere.md", pagina="bozza-paniere.html",
         titolo="Allegato annuale del Paniere di Sufficienza", nota="bozza 0.1"),
    dict(md="bozze/allegato-ucr.md", pagina="bozza-ucr.html",
         titolo="Allegato UCR e primo bilancio delle ore", nota="bozza 0.1"),
    dict(md="PROPOSTE.md", pagina="proposte.html",
         titolo="Proposte di modifica aperte", nota="in discussione", classe=""),
]


def segnalazioni(tipo):
    """Indirizzo dell'elenco delle segnalazioni aperte di un tipo."""
    from urllib.parse import quote
    return "%s/issues?q=%s" % (REPOSITORY, quote('is:issue state:open in:title "%s"' % SEGNALAZIONI[tipo]))

# Ogni lingua ha le proprie cartelle, i propri nomi di pagina e le proprie scritte.
LINGUE = {
    "it": dict(
        codice="it", prefisso="", nome_lingua="Italiano",
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
                           "per intero, citando la fonte, ma non modificarlo. Si può tradurre in altre lingue, se la "
                           "traduzione è integrale e fedele; per ridurlo o adattarlo serve il permesso degli "
                           "autori: vedi <a href=\"{con}\">come contribuire</a>.",
            avviso="",
            bozza="Bozza in verifica: non adottata, non sperimentata",
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
            comincia="Comincia dal percorso", vai_regole="Vai alle regole", prova_caso="Metti alla prova un caso",
            h_prova="Mettila alla prova",
            guida_prova="Il progetto ha bisogno di critiche più che di consensi. Tre modi per cominciare, ciascuno "
                        "con segnalazioni già aperte:",
            prova=[
                ("caso", "Prova un caso", "Prendi una situazione concreta, un conflitto o un’obiezione in Assemblea, e "
                                          "falla passare nelle procedure: dove reggono e dove no."),
                ("dato", "Verifica un dato", "Molte soglie sono proposte iniziali: da 30 a 500 persone per Comunità, il "
                                             "quorum, 50 litri d’acqua al giorno. Servono dati che le confermino o le "
                                             "smentiscano."),
                ("codice", "Controlla un Codice", "Se conosci una materia, leggi il Codice che la riguarda e di’ che "
                                                  "cosa è sbagliato, che cosa manca, che cosa non è applicabile."),
            ],
            senza_conto="Non hai un account su GitHub? Scrivi a {mail}: va bene anche una riga.",
            h_minuto="In un minuto",
            minuto=[
                ("Che cos’è", "Una proposta di organizzazione sociale scritta per intero: una Costituzione, 16 Codici "
                              "e 4 Allegati. Non è in vigore da nessuna parte."),
                ("È comunismo?", "Non nel senso che la parola ha preso nella storia. Qui non ci sono Stato, partito "
                                 "né potere centrale. Si entra per scelta e si esce quando si vuole. Ciò che è "
                                 "personale resta personale, e chi contribuisce di più è riconosciuto. Dalle "
                                 "tradizioni comuniste e anarchiche il progetto prende i beni comuni e l’essenziale "
                                 "garantito a tutti. Dalla tradizione dei diritti prende l’inviolabilità della "
                                 "persona e i limiti al potere. Dall’ecologia prende i limiti del pianeta. Non "
                                 "chiede di aderire a un’etichetta: chiede di essere giudicato sulle regole."),
                ("Come è fatta", "Comunità di base da 30 a 500 persone, che decidono in assemblea e si federano in "
                                 "livelli più ampi, fino al pianeta. Nessun livello comanda quello sotto. Gli "
                                 "incarichi sono assegnati per sorteggio tra volontari, durano poco e non si "
                                 "ripetono di seguito."),
                ("Che cosa garantisce", "A ogni membro casa, cibo, acqua, energia, cure, istruzione e connessione: "
                                        "non sono il compenso del lavoro. I beni si prendono dai Magazzini comuni "
                                        "secondo il bisogno; il denaro è abolito. Terra, acqua, energia e mezzi di "
                                        "produzione sono beni comuni, che non si comprano e non si vendono. Restano "
                                        "personali la casa in uso e i propri oggetti."),
                ("Che cosa chiede", "A ogni adulto che può, una quota a rotazione del lavoro necessario a tutti. E la "
                                    "rinuncia alla proprietà privata dei mezzi di produzione, all’accumulo, alle "
                                    "armi e allo sfruttamento degli animali, macellazione compresa. Chi non ci sta "
                                    "può uscire in qualsiasi momento e chiedere di rientrare."),
                ("Che cosa non sappiamo", "Se funziona. Nessuna comunità l’ha ancora messa alla prova. Molte soglie e "
                                          "quantità sono ipotesi da verificare. Come ci si arrivi dal sistema "
                                          "attuale, e se regga su grande scala, è scritto ma mai provato. Per questo "
                                          "tutto è pubblico e le regole si possono correggere."),
            ],
            h_percorso="Il percorso",
            guida_percorso="Quattro letture in sequenza: da dove veniamo, dove siamo, che cosa non funziona, "
                           "che cosa proponiamo.",
            h_regole="Le regole",
            guida_regole="La proposta è scritta per intero, articolo per articolo, perché possa essere "
                         "verificata e corretta.",
            codici_allegati="{nc} Codici e {na} Allegati tecnici", storico="storico",
            parametri="Parametri da verificare", parametri_nota="bozza di calibrazione",
            h_bozze="Bozze e proposte",
            bozze_sotto="Bozze degli allegati tecnici che i Codici citano e che non sono ancora stati adottati, e "
                        "modifiche di sostanza in discussione. Nessuna è in vigore.",
            reg_parametri="I numeri proposti, con la loro origine e la prova che servirebbe per confermarli, "
                          "sono nel <a href=\"{par}\">registro dei parametri da verificare</a>.",
            h_aperto="Un progetto aperto", h_stato="Stato", h_licenza="Licenza",
            stato="Il progetto è nella fase di scrittura e verifica. I testi non sono un modello dimostrato: "
                  "devono essere sperimentati, e dove falliscono vanno corretti.",
            licenza="Le regole sono libere: {lic}. Si possono copiare, modificare e ripubblicare, citando la "
                    "fonte e mantenendo la stessa licenza. I quattro testi del percorso si possono copiare e "
                    "ripubblicare per intero, ma non modificare: {licp}. Tradurli è permesso.",
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
        codice="en", prefisso="en/", nome_lingua="English",
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
                           "in full, citing the source, but may not modify it. It may be translated into other "
                           "languages, provided the translation is complete and faithful; abridging or "
                           "adapting it requires the authors’ permission: see "
                           "<a href=\"{con}\">how to contribute</a>.",
            avviso="This is a working translation. The Italian text is the authoritative one.",
            bozza="Draft under review: not adopted, not tested",
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
            comincia="Start with the path", vai_regole="Go to the rules", prova_caso="Put a case to the test",
            h_prova="Put it to the test",
            guida_prova="The project needs criticism more than approval. Three ways to start, each with issues already "
                        "open (in Italian for now; you can write in English):",
            prova=[
                ("caso", "Test a case", "Take a concrete situation, a conflict or an objection in the Assembly, and run "
                                        "it through the procedures: where they hold and where they do not."),
                ("dato", "Check a figure", "Many thresholds are initial proposals: 30 to 500 people per Community, the "
                                           "quorum, 50 litres of water a day. Data that confirm or refute them are "
                                           "needed."),
                ("codice", "Review a Code", "If you know a subject, read the Code that deals with it and say what is "
                                            "wrong, what is missing, what cannot be applied."),
            ],
            senza_conto="No GitHub account? Write to {mail}: even one line is fine.",
            h_minuto="In one minute",
            minuto=[
                ("What it is", "A proposal for organising society, written out in full: a Constitution, 16 Codes and "
                               "4 Annexes. It is not in force anywhere."),
                ("Is it communism?", "Not in the sense the word has taken on in history. Here there is no State, "
                                     "no party and no central power. People join by choice and leave when they "
                                     "wish. What is personal stays personal, and those who contribute more are "
                                     "recognised. From the communist and anarchist traditions the project takes "
                                     "the commons and the guarantee of the essentials for all. From the tradition "
                                     "of rights it takes the inviolability of the person and the limits on power. "
                                     "From ecology it takes the limits of the planet. It does not ask anyone to "
                                     "sign up to a label: it asks to be judged on its rules."),
                ("How it is built", "Base Communities of 30 to 500 people, which decide in assembly and federate into "
                                    "wider levels, up to the planet. No level commands the one below. Roles are "
                                    "assigned by lot among volunteers, last a short time and cannot be held twice "
                                    "in a row."),
                ("What it guarantees", "To every member a home, food, water, energy, health care, education and "
                                       "connectivity: these are not payment for work. Goods are taken from the "
                                       "Common Storehouses according to need; money is abolished. Land, water, "
                                       "energy and the means of production are commons, which cannot be bought or "
                                       "sold. The home one lives in and one’s own belongings remain personal."),
                ("What it asks", "Of every adult who is able, a rotating share of the work everyone needs. And "
                                 "giving up private ownership of the means of production, accumulation, weapons "
                                 "and the exploitation of animals, slaughter included. Anyone who does not agree "
                                 "can leave at any time and ask to come back."),
                ("What we do not know", "Whether it works. No community has put it to the test yet. Many thresholds "
                                        "and quantities are hypotheses to be verified. How to get there from the "
                                        "present system, and whether it holds at large scale, is written but never "
                                        "tried. This is why everything is public and the rules can be corrected."),
            ],
            h_percorso="The path",
            guida_percorso="Four readings in sequence: where we come from, where we are, what does not work, "
                           "what we propose.",
            h_regole="The rules",
            guida_regole="The proposal is written out in full, article by article, so that it can be "
                         "verified and corrected.",
            codici_allegati="{nc} Codes and {na} Technical Annexes", storico="history",
            parametri="Parameters to be verified", parametri_nota="calibration draft · in Italian",
            h_bozze="Drafts and proposals (in Italian)",
            bozze_sotto="Drafts of the technical annexes that the Codes refer to and that have not yet been "
                        "adopted, and substantive changes under discussion. None is in force.",
            reg_parametri="The proposed numbers, with their origin and the test each would need, are in the "
                          "<a href=\"{par}\">register of parameters to be verified</a> (for now in Italian).",
            h_aperto="An open project", h_stato="Status", h_licenza="Licence",
            stato="The project is at the stage of writing and verification. The texts are not a proven "
                  "model: they must be tested, and corrected where they fail.",
            licenza="The rules are free: {lic}. They may be copied, modified and republished, citing the "
                    "source and keeping the same licence. The four texts of the path may be copied and "
                    "republished in full, but not modified: {licp}. Translating them is permitted.",
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
    "es": dict(
        codice="es", prefisso="es/", nome_lingua="Español", regole_da="it",
        nome="Proyecto de los Círculos",
        dir_percorso="recorrido", dir_registro="registro", dir_scarica="es/descargas",
        pag_modifiche="cambios.html", pag_contribuire="contribuir.html",
        md_modifiche="", md_contribuire="CONTRIBUIR.md",
        licenza_url="https://creativecommons.org/licenses/by-sa/4.0/deed.es",
        licenza_percorso_url="https://creativecommons.org/licenses/by-nd/4.0/deed.es",
        livelli=[("Núcleo de cuidado", "de 1 a 15 personas", ["cuidado cotidiano", "y hospitalidad"]),
                 ("Comunidad de base", "por norma 30–500 personas", ["decide en Asamblea,", "gestiona trabajo y Almacén"]),
                 ("Cuenca", "por norma ≥ 3 Comunidades", ["logística, hospital,", "Tribunal de Garantía"]),
                 ("Biorregión", "varias Cuencas", ["ferrocarriles, energía,", "alta especialización"]),
                 ("Círculo global", "toda la humanidad", ["reglas técnicas comunes,", "ningún gobierno"])],
        ciclo=[("Necesidades", ["lo que necesitan", "las personas"]),
               ("Asamblea", ["todas las personas,", "un voto cada una"]),
               ("Trabajo necesario", ["por rotación; en promedio", "no más de 15 horas", "a la semana"]),
               ("Almacenes comunes", ["bienes y servicios", "de todos"]),
               ("Acceso", ["a cada cual", "según su necesidad"])],
        frecce=["detectadas", "decide", "produce", "dan"],
        maiuscole=["Confederación", "Círculos", "Código", "Annex", "Asamblea", "Red", "Almacenes Comunes",
                   "Contribución Básica Obligatoria"],
        t=dict(
            salta="Ir al contenido", sezioni="Secciones", percorso="Recorrido", registro="Reglas",
            contribuire="Contribuir", repository="Repositorio",
            piede="La Constitución, los Códigos y los Anexos se publican con licencia {lic}: cualquiera puede "
                  "copiarlos, modificarlos y volver a publicarlos, citando la fuente y manteniendo la misma "
                  "licencia. Los cuatro textos del recorrido se publican con licencia {licp}: pueden copiarse y "
                  "volver a publicarse íntegros, citando la fuente, pero no modificarse.",
            piede_registro="Este texto se publica con licencia {lic}: cualquiera puede copiarlo, modificarlo y "
                           "volver a publicarlo, citando la fuente y manteniendo la misma licencia.",
            piede_percorso="Este texto se publica con licencia {licp}: cualquiera puede copiarlo y volver a "
                           "publicarlo íntegro, citando la fuente, pero no modificarlo. Puede traducirse a otras "
                           "lenguas, si la traducción es íntegra y fiel; para abreviarlo o adaptarlo hace falta el "
                           "permiso de los autores: consulta <a href=\"{con}\">cómo contribuir</a>.",
            avviso="Esta es una traducción de trabajo. El texto de referencia es el italiano.",
            bozza="Borrador en revisión: no adoptado, no puesto a prueba",
            modifiche="Registro de cambios", come_contribuire="Cómo contribuir",
            capitolo="Capítulo {n} de {tot} · {min} min de lectura",
            continua="Continúa · capítulo {n} de {tot}",
            fine="El recorrido termina aquí", leggi_regole="Lee las reglas",
            fine_testo="La Constitución, los dieciséis Códigos y los Anexos, con todas sus versiones. Por ahora "
                       "en italiano y en inglés.",
            inizio="← Inicio", capitoli="Capítulos", scarica="Descargar", indice="Índice",
            indice_aria="Índice del texto",
            allineamento="Versiones de los demás textos con los que está alineado",
            reg_sotto="Todos los textos normativos del proyecto, con su versión. Cada cambio se anota y se "
                      "motiva en el <a href=\"{mod}\">registro de cambios</a>.",
            h_cost="Constitución", h_codici="Códigos", h_allegati="Anexos técnicos",
            h_come="Cómo están organizados",
            come="La Constitución establece los principios y la estructura general. Los Códigos transforman esos "
                 "principios en reglas operativas. Los Anexos técnicos desarrollan procedimientos, criterios y "
                 "especificaciones. En caso de conflicto prevalece la Constitución.",
            desc_reg="Constitución, Códigos y Anexos del Proyecto de los Círculos, con todas sus versiones.",
            versione="versión",
            etichetta="Una propuesta abierta", domanda="¿Qué alternativas tenemos?",
            attacco="El Proyecto de los Círculos es una propuesta de alternativa al modo en que hoy organizamos "
                    "la vida colectiva. Empieza por la persona, organiza la colectividad y construye los "
                    "instrumentos para que ninguna de las dos tenga que dominar a la otra.",
            comincia="Empieza por el recorrido", vai_regole="Ir a las reglas", prova_caso="Pon a prueba un caso",
            h_prova="Ponla a prueba",
            guida_prova="El proyecto necesita críticas más que adhesiones. Tres maneras de empezar, cada una con "
                        "incidencias ya abiertas (por ahora en italiano; puedes escribir en español):",
            prova=[
                ("caso", "Prueba un caso", "Toma una situación concreta, un conflicto o una objeción en la Asamblea, y "
                                           "sométela a los procedimientos: dónde resisten y dónde no."),
                ("dato", "Verifica un dato", "Muchos umbrales son propuestas iniciales: de 30 a 500 personas por "
                                             "Comunidad, el quórum, 50 litros de agua al día. Hacen falta datos que "
                                             "los confirmen o los desmientan."),
                ("codice", "Revisa un Código", "Si conoces una materia, lee el Código que la trata y di qué está mal, "
                                               "qué falta, qué no es aplicable."),
            ],
            senza_conto="¿No tienes cuenta de GitHub? Escribe a {mail}: basta con una línea.",
            h_minuto="En un minuto",
            minuto=[
                ("Qué es", "Una propuesta de organización social escrita por entero: una Constitución, 16 Códigos y "
                           "4 Anexos. No está en vigor en ninguna parte."),
                ("¿Es comunismo?", "No en el sentido que la palabra ha adquirido en la historia. Aquí no hay Estado, "
                                   "ni partido, ni poder central. Se entra por elección y se sale cuando se quiere. "
                                   "Lo personal sigue siendo personal, y a quien contribuye más se le reconoce. De "
                                   "las tradiciones comunista y anarquista el proyecto toma los bienes comunes y lo "
                                   "esencial garantizado a todos. De la tradición de los derechos toma la "
                                   "inviolabilidad de la persona y los límites al poder. De la ecología toma los "
                                   "límites del planeta. No pide adherirse a una etiqueta: pide ser juzgado por "
                                   "sus reglas."),
                ("Cómo está hecha", "Comunidades de base de 30 a 500 personas, que deciden en asamblea y se federan "
                                    "en niveles más amplios, hasta el planeta. Ningún nivel manda sobre el de abajo. "
                                    "Los cargos se asignan por sorteo entre voluntarios, duran poco y no se repiten "
                                    "de forma consecutiva."),
                ("Qué garantiza", "A cada miembro vivienda, alimentos, agua, energía, atención sanitaria, educación "
                                  "y conexión: no son la retribución del trabajo. Los bienes se toman de los Almacenes "
                                  "comunes según la necesidad; el dinero queda abolido. Tierra, agua, energía y "
                                  "medios de producción son bienes comunes, que no se compran ni se venden. Siguen "
                                  "siendo personales la vivienda en uso y los objetos propios."),
                ("Qué pide", "A cada adulto que pueda, una parte por rotación del trabajo necesario para todos. Y la "
                             "renuncia a la propiedad privada de los medios de producción, a la acumulación, a las "
                             "armas y a la explotación de los animales, incluido su sacrificio. Quien no esté de "
                             "acuerdo puede salir en cualquier momento y pedir volver."),
                ("Qué no sabemos", "Si funciona. Ninguna comunidad la ha puesto a prueba todavía. Muchos umbrales y "
                                   "cantidades son hipótesis por verificar. Cómo se llega desde el sistema actual, y "
                                   "si resiste a gran escala, está escrito pero nunca se ha probado. Por eso todo es "
                                   "público y las reglas se pueden corregir."),
            ],
            h_percorso="El recorrido",
            guida_percorso="Cuatro lecturas en secuencia: de dónde venimos, dónde estamos, qué no funciona, "
                           "qué proponemos.",
            h_regole="Las reglas",
            guida_regole="La propuesta está escrita por entero, artículo por artículo, para que pueda verificarse "
                         "y corregirse. Las reglas están por ahora en italiano y en inglés.",
            codici_allegati="{nc} Códigos y {na} Anexos técnicos", storico="historial",
            parametri="Parámetros por verificar", parametri_nota="borrador de calibración · en italiano",
            h_bozze="Borradores y propuestas (en italiano)",
            bozze_sotto="Borradores de los anexos técnicos que los Códigos citan y que todavía no se han adoptado, "
                        "y cambios de fondo en discusión. Ninguno está en vigor.",
            reg_parametri="Los números propuestos, con su origen y la prueba que haría falta para confirmarlos, "
                          "están en el <a href=\"{par}\">registro de parámetros por verificar</a> (por ahora en italiano).",
            h_aperto="Un proyecto abierto", h_stato="Estado", h_licenza="Licencia",
            stato="El proyecto está en la fase de escritura y verificación. Los textos no son un modelo "
                  "demostrado: deben ponerse a prueba, y corregirse allí donde fallen.",
            licenza="Las reglas son libres: {lic}. Pueden copiarse, modificarse y volver a publicarse, citando la "
                    "fuente y manteniendo la misma licencia. Los cuatro textos del recorrido pueden copiarse y "
                    "volver a publicarse íntegros, pero no modificarse: {licp}. Traducirlos está permitido.",
            contribuire_testo="Leer, criticar, verificar, corregir. Hacen falta competencias distintas y casos "
                              "concretos con los que poner a prueba las reglas.",
            desc_home="Una propuesta abierta de alternativa al modo en que organizamos la vida colectiva: "
                      "el recorrido, la Constitución, los Códigos.",
            figura="Personas dispuestas en círculo, todas iguales, con otras comunidades conectadas alrededor",
            si_uniscono="se unen en",
            ritorno="nacen nuevas necesidades, y el ciclo vuelve a empezar",
            consigli="Consejos técnicos e IA", consigli2="proponen y calculan, no deciden",
            garanzia="Círculo de Garantía", garanzia2="controla y recibe las apelaciones; cargos breves, por sorteo",
            did_livelli="Los cinco niveles, de la persona al planeta. Ningún nivel manda sobre el de abajo: cada "
                        "decisión se queda en el nivel más cercano que pueda tomarla.",
            did_ciclo="Cómo funciona una Comunidad: se parte de las necesidades, la Asamblea decide, el trabajo "
                      "necesario llena los Almacenes y cada cual accede según su necesidad.",
        ),
    ),
}


# ----------------------------------------------------------------- lettura

def ha_registro(lingua):
    """Vero se la lingua ha i propri testi normativi (Costituzione, Codici, Allegati)."""
    return bool(glob.glob(os.path.join(TESTI, lingua["codice"], lingua["dir_registro"], "*.md")))


def lingua_regole(lingua):
    """La lingua in cui si leggono le regole: la propria, oppure quella indicata in «regole_da»."""
    return lingua if ha_registro(lingua) else LINGUE[lingua["regole_da"]]


def url_parametri(lingua, profondita=0):
    """Indirizzo del registro dei parametri, visto da una pagina della lingua a una certa profondità."""
    lp = LINGUE[PARAMETRI["lingua"]]
    su = "../" * (lingua["prefisso"].count("/") + profondita)
    return "%s%s%s/%s" % (su, lp["prefisso"], lp["dir_registro"], PARAMETRI["pagina"])


def dir_regole(lingua):
    """Cartella delle regole, relativa alla radice della lingua."""
    lr = lingua_regole(lingua)
    if lr is lingua:
        return lingua["dir_registro"]
    return "../" * lingua["prefisso"].count("/") + lr["prefisso"] + lr["dir_registro"]


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
    # un paragrafo tutto in grassetto ("In breve") seguito da un elenco, in apertura, diventa un riquadro di sintesi
    corpo = re.sub(r'\A\s*<p><strong>([^<]{1,40})</strong></p>\s*<ul>(.*?)</ul>',
                   r'<aside class="inbreve"><p class="inbreve-titolo">\1</p><ul>\2</ul></aside>', corpo, count=1, flags=re.S)
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


def pagina(lingua, titolo, descrizione, corpo, profondita, sezione="", gemelle=None):
    """Avvolge il corpo nella pagina completa.

    profondita: quante cartelle separano la pagina dalla radice della lingua (0 o 1).
    gemelle:    per ogni altra lingua, l'indirizzo (relativo alla radice del sito) della stessa pagina.
    """
    t = lingua["t"]
    radice = "../" * profondita                                   # radice della lingua
    base = radice + ("../" * lingua["prefisso"].count("/"))       # radice del sito

    def voce(nome, indirizzo, chiave):
        attuale = ' aria-current="page"' if chiave == sezione else ""
        return '<a href="%s%s"%s>%s</a>' % (radice, indirizzo, attuale, nome)

    cambio = "".join('<a class="lingua" href="%s%s" lang="%s" hreflang="%s">%s</a>'
                     % (base, indirizzo, c, c, LINGUE[c]["nome_lingua"]) for c, indirizzo in (gemelle or {}).items())
    deposito = (' · <a href="%s">%s</a>' % (html.escape(REPOSITORY), t["repository"])) if REPOSITORY else ""
    avviso = ('<p class="avviso" role="note">%s</p>' % t["avviso"]) if t["avviso"] else ""
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
%(avviso)s
<main id="contenuto">
%(corpo)s
</main>
<footer class="piede">
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
           piede=piede, reg=dir_regole(lingua), pmod=lingua_regole(lingua)["pag_modifiche"],
           pcon=lingua["pag_contribuire"], modifiche=t["modifiche"], come=t["come_contribuire"],
           deposito=deposito,
           v1=voce(t["percorso"], "index.html#percorso", "percorso"),
           v2=voce(t["registro"], dir_regole(lingua) + "/index.html", "registro"),
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


def costruisci_lingua(lingua, altre):
    """Costruisce tutte le pagine di una lingua. `altre` sono le altre lingue presenti, per i collegamenti tra le versioni."""
    t = lingua["t"]
    nome = lingua["nome"]
    percorso, registro = carica(lingua)
    proprie = bool(registro)                     # la lingua ha le proprie regole?
    lreg = lingua_regole(lingua)
    if not proprie:
        registro = carica(lreg)[1]               # servono solo per i conteggi e i collegamenti
    # indirizzi delle pagine gemelle nelle altre lingue, per identificativo comune
    tavole = {}
    for altra in altre:
        p2, r2 = carica(altra)
        tavola = {}
        for meta, _ in p2:
            tavola[meta["id"]] = "%s%s/%s.html" % (altra["prefisso"], altra["dir_percorso"], meta["slug"])
        for meta, _ in r2:
            tavola[meta["id"]] = "%s%s/%s.html" % (altra["prefisso"], altra["dir_registro"], meta["slug"])
        tavole[altra["codice"]] = tavola

    def gemelle(chiave="", predefinite=None):
        """La stessa pagina nelle altre lingue; dove non esiste, la pagina iniziale di quella lingua."""
        return dict((a["codice"], tavole[a["codice"]].get(chiave) or (predefinite or {}).get(a["codice"])
                     or "%sindex.html" % a["prefisso"]) for a in altre)
    costituzione = next(m for m, _ in registro if m["gruppo"] == "costituzione")
    dp, dr = lingua["dir_percorso"], dir_regole(lingua)

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
                      gemelle(meta["id"])))

    # --- testi del registro (solo se la lingua ha le proprie regole)
    for meta, testo in (registro if proprie else []):
        sommario, corpo = pandoc(abbassa_titoli(testo), indice=True, etichetta=t["indice_aria"])
        dettagli = ""
        if meta.get("allineamento"):
            dettagli = ('<details class="allineamento"><summary>%s</summary><p>%s</p></details>'
                        % (t["allineamento"], html.escape(meta["allineamento"])))
        contenuto = """<article class="norma">
<header class="apertura">
  <p class="briciole"><a href="index.html">%(registro)s</a> / %(breve)s</p>
  <h1>%(titolo)s</h1>
  <p class="dati"><span class="versione">%(versione)s</span><span class="stato">%(bozza)s</span>%(scarica)s</p>
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
                     versione=meta["versione"], bozza=t["bozza"], scarica=scaricabili(lingua, meta["slug"], 1),
                     dettagli=dettagli, sommario=sommario, corpo=corpo)
        scrivi(lingua, "%s/%s.html" % (dr, meta["slug"]),
               pagina(lingua, "%s — %s" % (meta["breve"], nome),
                      "%s, %s %s." % (meta["breve"], t["versione"], meta["versione"]),
                      contenuto, 1, "registro", gemelle(meta["id"])))

    # --- indice del registro
    base_bozze = url_parametri(lingua, 1).rsplit("/", 1)[0]
    bozze = '<h2>%s</h2>\n<p>%s</p>\n<ul class="testi">%s</ul>' % (
        t["h_bozze"], t["bozze_sotto"],
        "\n".join('<li><a href="%s/%s">%s</a><span class="versione">%s</span></li>'
                  % (base_bozze, b["pagina"], html.escape(b["titolo"]), b["nota"]) for b in BOZZE))

    def elenco(gruppo):
        return "\n".join('<li><a href="%s.html">%s</a><span class="versione">%s</span></li>'
                         % (m["slug"], html.escape(m["breve"]), m["versione"])
                         for m, _ in registro if m["gruppo"] == gruppo)
    contenuto = """<section class="foglio">
<header class="apertura">
  <h1>%s</h1>
  <p class="sottotitolo">%s %s</p>
  <p><span class="stato">%s</span></p>
</header>
<h2>%s</h2>
<ul class="testi">%s</ul>
<h2>%s</h2>
<ul class="testi">%s</ul>
<h2>%s</h2>
<ul class="testi">%s</ul>
<h2>%s</h2>
<p>%s</p>
%s
</section>""" % (t["registro"], t["reg_sotto"].format(mod=lingua["pag_modifiche"]),
                 t["reg_parametri"].format(par=url_parametri(lingua, 1)), t["bozza"], t["h_cost"],
                 elenco("costituzione"), t["h_codici"], elenco("codici"), t["h_allegati"], elenco("allegati"),
                 t["h_come"], t["come"], bozze)
    if proprie:
        scrivi(lingua, "%s/index.html" % dr,
               pagina(lingua, "%s — %s" % (t["registro"], nome), t["desc_reg"], contenuto, 1, "registro",
                      gemelle("", dict((a["codice"], "%s%s/index.html" % (a["prefisso"], a["dir_registro"]))
                                       for a in altre if ha_registro(a)))))

    # --- pagine di servizio: modifiche, contribuire
    servizio = [
        (lingua["md_contribuire"], lingua["pag_contribuire"], t["come_contribuire"], 0, "contribuire",
         dict((a["codice"], "%s%s" % (a["prefisso"], a["pag_contribuire"])) for a in altre), ""),
    ]
    if lingua["codice"] == PARAMETRI["lingua"]:
        servizio.append((PARAMETRI["md"], "%s/%s" % (dr, PARAMETRI["pagina"]), t["parametri"], 1, "registro", {},
                         " largo"))
        for b in BOZZE:
            servizio.append((b["md"], "%s/%s" % (dr, b["pagina"]), b["titolo"], 1, "registro", {},
                             b.get("classe", " largo")))
    if proprie:
        servizio.append(
            (lingua["md_modifiche"], "%s/%s" % (dr, lingua["pag_modifiche"]), t["modifiche"], 1, "registro",
             dict((a["codice"], "%s%s/%s" % (a["prefisso"], a["dir_registro"], a["pag_modifiche"]))
                  for a in altre if ha_registro(a)), ""))
    for origine, destinazione, titolo, profondita, sezione, gem, classe in servizio:
        testo = open(os.path.join(RADICE, origine), encoding="utf-8").read()
        testo = re.sub(r"\A# .*\n", "", testo)
        _, corpo = pandoc(abbassa_titoli(testo))
        contenuto = ('<article class="foglio%s"><header class="apertura"><h1>%s</h1></header>'
                     '<div class="prosa">%s</div></article>' % (classe, titolo, corpo))
        scrivi(lingua, destinazione,
               pagina(lingua, "%s — %s" % (titolo, nome), titolo + ".", contenuto, profondita, sezione, gemelle("", gem)))

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
    <p><span class="stato">%(bozza)s</span></p>
    <p class="azioni"><a class="bottone" href="%(dp)s/%(primo)s.html">%(comincia)s</a><a class="secondario" href="%(dr)s/index.html">%(vai)s</a><a class="secondario" href="%(url_caso)s">%(prova_caso)s</a></p>
  </div>
  %(figura)s
</section>

<section class="blocco minuto" aria-labelledby="minuto">
  <h2 id="minuto">%(h_minuto)s</h2>
  <dl>
%(minuto)s
  </dl>
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
    <li><a href="%(upar)s">%(parametri)s</a><span class="versione">%(parametri_nota)s</span></li>
  </ul>
</section>

<section id="prova" class="blocco">
  <h2>%(h_prova)s</h2>
  <p class="guida">%(guida_prova)s</p>
  <div class="tre">
%(prova)s
  </div>
  <p class="senza-conto">%(senza_conto)s</p>
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
        h_minuto=t["h_minuto"], url_caso=segnalazioni("caso"), prova_caso=t["prova_caso"], h_prova=t["h_prova"],
        guida_prova=t["guida_prova"],
        prova="\n".join('    <div><h3><a href="%s">%s</a></h3><p>%s</p></div>'
                        % (html.escape(segnalazioni(k)), html.escape(a), html.escape(b)) for k, a, b in t["prova"]),
        senza_conto=t["senza_conto"].format(mail='<a href="mailto:%s">%s</a>' % (CONTATTO, CONTATTO)),
        minuto="\n".join("    <div><dt>%s</dt><dd>%s</dd></div>" % (html.escape(a), html.escape(b)) for a, b in t["minuto"]),
        h_percorso=t["h_percorso"], guida_percorso=t["guida_percorso"], passi=passi, h_regole=t["h_regole"],
        guida_regole=t["guida_regole"], cost=costituzione["slug"], h_cost=t["h_cost"],
        vcost=costituzione["versione"], codall=t["codici_allegati"].format(nc=nc, na=na),
        registro=t["registro"].lower(), pmod=lreg["pag_modifiche"], modifiche=t["modifiche"],
        upar=url_parametri(lingua), parametri=t["parametri"], parametri_nota=t["parametri_nota"],
        storico=t["storico"], h_aperto=t["h_aperto"], h_stato=t["h_stato"], stato=t["stato"], bozza=t["bozza"],
        h_licenza=t["h_licenza"], licenza=t["licenza"].format(lic=licenza, licp=licenza_p), contribuire=t["contribuire"],
        ctesto=t["contribuire_testo"], pcon=lingua["pag_contribuire"], come=t["come_contribuire"])
    scrivi(lingua, "index.html",
           pagina(lingua, nome, t["desc_home"], contenuto, 0, "", gemelle()))


def costruisci():
    presenti = [c for c in LINGUE if os.path.isdir(os.path.join(TESTI, c))]
    for codice in presenti:
        costruisci_lingua(LINGUE[codice], [LINGUE[c] for c in presenti if c != codice])
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
