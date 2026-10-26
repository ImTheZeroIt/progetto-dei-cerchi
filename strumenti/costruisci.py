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

import ricerca

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

# Per i motori di ricerca: titolo della pagina iniziale e descrizione delle pagine delle regole, per lingua.
TITOLO_HOME = {
    "it": "Progetto dei Cerchi — Confederazione dei Cerchi: Costituzione e Codici",
    "en": "The Circles Project — Confederation of Circles: Constitution and Codes",
    "fr": "Projet des Cercles — Confédération des Cercles\u202f: Constitution et Codes",
    "es": "Proyecto de los Círculos — Confederación de los Círculos",
}
DESC_REGOLA = {
    "it": "{breve}: testo completo, versione {v}. Fa parte delle regole della Confederazione dei Cerchi, "
          "una proposta aperta di società senza potere centrale.",
    "en": "{breve}: full text, version {v}. Part of the rules of the Confederation of Circles, "
          "an open proposal for a society without central power.",
    "fr": "{breve}\u202f: texte intégral, version {v}. Fait partie des règles de la Confédération des Cercles, "
          "une proposition ouverte de société sans pouvoir central.",
    "es": "{breve}: texto completo, versión {v}. Forma parte de las reglas de la Confederación de los Círculos, "
          "una propuesta abierta de sociedad sin poder central.",
}

# Indirizzo a cui scrivere per chi non ha un account sul repository.
CONTATTO = "zerocirclesproject@gmail.com"

# Parole con cui cominciano i titoli delle segnalazioni aperte, per tipo: servono ai tre inviti della pagina iniziale.
SEGNALAZIONI = {"caso": "Caso di prova", "dato": "Parametro da confermare", "codice": "Verifica di competenza"}


# Registro dei parametri da verificare, per lingua. Le lingue che non lo hanno rimandano a quello italiano.
PARAMETRI = {
    "it": dict(md="PARAMETRI.md", pagina="parametri.html"),
    "en": dict(md="testi/en/drafts/parameters.md", pagina="parameters.html"),
    "fr": dict(md="testi/fr/brouillons/parametres.md", pagina="parametres.html"),
}

# Bozze e proposte: allegati tecnici che i Codici citano e che non sono ancora adottati, proposte di modifica.
# Ogni voce ha una chiave comune a tutte le lingue (serve al cambio di lingua); le lingue senza traduzione
# rimandano all'italiano.
BOZZE = {
    "it": [
        dict(chiave="paniere", md="bozze/allegato-paniere.md", pagina="bozza-paniere.html",
             titolo="Allegato annuale del Paniere di Sufficienza", nota="bozza 0.1"),
        dict(chiave="ucr", md="bozze/allegato-ucr.md", pagina="bozza-ucr.html",
             titolo="Allegato UCR e primo bilancio delle ore", nota="bozza 0.1"),
        dict(chiave="cdr", md="bozze/tabella-cdr.md", pagina="bozza-cdr.html",
             titolo="Tabella pubblica del CdR", nota="bozza 0.1"),
        dict(chiave="proposte", md="PROPOSTE.md", pagina="proposte.html",
             titolo="Proposte di modifica (archivio)", nota="accolte il 19 ottobre 2026", classe=""),
        dict(chiave="verifica", md="VERIFICA-PROPOSTE.md", pagina="verifica-proposte.html",
             titolo="Verifica contraria delle proposte", nota="sulla versione 1", classe=""),
        dict(chiave="coerenza", md="VERIFICA-COERENZA.md", pagina="verifica-coerenza.html",
             titolo="Verifica di coerenza delle regole", nota="19 ottobre 2026", classe=""),
    ],
    "en": [
        dict(chiave="paniere", md="testi/en/drafts/draft-basket.md", pagina="draft-basket.html",
             titolo="Annual Annex of the Sufficiency Basket", nota="draft 0.1"),
        dict(chiave="ucr", md="testi/en/drafts/draft-ucr.md", pagina="draft-ucr.html",
             titolo="UCR Annex and first balance of hours", nota="draft 0.1"),
        dict(chiave="cdr", md="testi/en/drafts/draft-cdr.md", pagina="draft-cdr.html",
             titolo="Public CdR table", nota="draft 0.1"),
        dict(chiave="proposte", md="testi/en/drafts/proposals.md", pagina="proposals.html",
             titolo="Change proposals (archive)", nota="accepted on 19 October 2026", classe=""),
        dict(chiave="verifica", md="testi/en/drafts/proposals-review.md", pagina="proposals-review.html",
             titolo="Adversarial review of the proposals", nota="on version 1", classe=""),
    ],
    "fr": [
        dict(chiave="paniere", md="testi/fr/brouillons/brouillon-panier.md", pagina="brouillon-panier.html",
             titolo="Annexe annuelle du Panier de suffisance", nota="brouillon 0.1"),
        dict(chiave="ucr", md="testi/fr/brouillons/brouillon-ucr.md", pagina="brouillon-ucr.html",
             titolo="Annexe UCR et premier bilan des heures", nota="brouillon 0.1"),
        dict(chiave="cdr", md="testi/fr/brouillons/brouillon-cdr.md", pagina="brouillon-cdr.html",
             titolo="Barème public de la CdR", nota="brouillon 0.1"),
        dict(chiave="proposte", md="testi/fr/brouillons/propositions.md", pagina="propositions.html",
             titolo="Propositions de modification (archives)", nota="acceptées le 19 octobre 2026", classe=""),
        dict(chiave="verifica", md="testi/fr/brouillons/verification-propositions.md",
             pagina="verification-propositions.html",
             titolo="Vérification contradictoire des propositions", nota="sur la version 1", classe=""),
    ],
}


# Ancore degli articoli, per lingua: servono a controllare i richiami delle domande frequenti.
ANCORE = {}


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
            attacco="Il Progetto dei Cerchi nasce dal rifiuto delle ingiustizie del mondo di oggi, e propone un altro "
                    "modo di vivere insieme. Comincia dalla persona, organizza la collettività e costruisce gli "
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
                ("Perché", "Perché le ingiustizie del mondo di oggi non sono eccezioni, ma il risultato ordinario del modo in cui è organizzato. Un sistema che misura il valore in profitto tratta il lavoro delle persone e le risorse del pianeta come costi da ridurre: così lo sfruttamento diventa la regola, non l’abuso. Il potere di usare la forza resta concentrato negli Stati, che lo rivolgono contro chi dissente al loro interno e contro altri popoli nelle guerre. E chi esercita il potere, economico o politico, risponde raramente delle conseguenze delle proprie decisioni. Intanto il sistema produce molto, ma non trasforma quella ricchezza in sicurezza, tempo e libertà di scelta per le persone: chi decide, chi guadagna e chi paga sono sempre più spesso persone diverse, e il presente si paga scaricando i costi sul futuro. Per questo correggere gli effetti non basta: bisogna cambiare le condizioni che li producono. È da qui che nasce questo progetto."),
                ("Che cos’è", "Un sistema completo per vivere insieme senza che nessuno domini gli altri. Non è un manifesto: è scritto per intero, regola per regola, in una Costituzione e nei Codici che la mettono in pratica, dalla casa alla giustizia, dal lavoro all’energia. Può nascere dentro la società di oggi, collegando le comunità solidali che esistono già senza chiedere loro di cambiare il proprio modo di vivere. Per ora è una proposta: non è in vigore da nessuna parte."),
                ("Che cosa garantisce", "A ogni membro casa, cibo, acqua, energia, cure, istruzione e connessione. Il patto è semplice: chi può lavora una parte del necessario per tutti, e in cambio ha ciò che gli serve per vivere. Non si riceve in proporzione alle ore: si prende dai Magazzini comuni secondo il bisogno, e chi non può lavorare, per età, malattia o disabilità, riceve lo stesso. Tra i membri non circola denaro. Ciò che è personale resta personale."),
                ("Che cosa chiede", "Di fare la propria parte e di rinunciare a ciò che permette di dominare gli altri. La propria parte è il lavoro necessario a tutti, diviso a rotazione tra chi può, perché a ciascuno ne resti poco. La rinuncia riguarda la proprietà privata della terra e dei mezzi di produzione, l’accumulo, le armi e lo sfruttamento degli animali. Chi non è d’accordo può andarsene quando vuole."),
                ("Chi decide", "Decidono le persone, direttamente, il più vicino possibile a dove vivono. Ogni decisione si prende al livello più piccolo capace di prenderla: la vita privata resta di ciascuno; ciò che riguarda tutti si decide insieme, nella propria Comunità; ciò che riguarda più Comunità si coordina in cerchi più ampi, che coordinano ma non comandano. Ognuno vota per sé, senza deleghe. Non ci sono capi né politici di mestiere: chi coordina è scelto a sorte tra chi si offre, per un tempo limitato, e risponde a chi gli ha affidato l’incarico."),
                ("Che cosa non sappiamo", "Se funziona: nessuna comunità l’ha ancora provata, e molti numeri sono ipotesi da verificare. Per questo tutto è pubblico e le regole si possono correggere."),
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
            desc_home="Nato dal rifiuto delle ingiustizie di oggi, una proposta aperta di alternativa al modo in cui organizziamo la vita collettiva: "
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
            attacco="The Circles Project is born of a refusal of the injustices of today’s world, and proposes another "
                    "way of living together. It starts from the person, organises the collectivity and builds the tools "
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
                ("Why", "Because the injustices of today’s world are not exceptions but the ordinary result of the way it is organised. A system that measures value in profit treats people’s work and the planet’s resources as costs to be cut: so exploitation becomes the rule, not the abuse. The power to use force remains concentrated in States, which turn it against those who dissent at home and against other peoples in war. And those who hold power, economic or political, rarely answer for the consequences of their decisions. Meanwhile the system produces a great deal, but does not turn that wealth into security, time and freedom of choice for people: those who decide, those who profit and those who pay are more and more often different people, and the present is paid for by shifting the costs onto the future. That is why correcting the effects is not enough: the conditions that produce them must change. This is where this project comes from."),
                ("What it is", "A complete system for living together without anyone dominating others. It is not a manifesto: it is written out in full, rule by rule, in a Constitution and in the Codes that put it into practice, from housing to justice, from work to energy. It can take root within today’s society, linking up the solidarity communities that already exist without asking them to change their way of life. For now it is a proposal: it is not in force anywhere."),
                ("What it guarantees", "To every member a home, food, water, energy, health care, education and connectivity. The deal is simple: those who can work a share of what everyone needs, and in return have what they need to live. Nothing is received in proportion to hours worked: goods are taken from the Common Storehouses according to need, and those who cannot work, because of age, illness or disability, receive the same. No money circulates among members. What is personal stays personal."),
                ("What it asks", "To do one’s share and to give up what makes it possible to dominate others. One’s share is the work everyone needs, divided in rotation among those who can, so that little falls to each. Giving up means private ownership of land and the means of production, accumulation, weapons and the exploitation of animals. Anyone who disagrees can leave whenever they wish."),
                ("Who decides", "People decide, directly, as close as possible to where they live. Every decision is taken at the smallest level able to take it: private life remains each person’s own; what concerns everyone is decided together, in one’s own Community; what concerns several Communities is coordinated in wider circles, which coordinate but do not command. Everyone votes for themselves, with no proxies. There are no leaders and no professional politicians: those who coordinate are chosen by lot among volunteers, for a limited time, and answer to those who entrusted them with the task."),
                ("What we do not know", "Whether it works: no community has tried it yet, and many numbers are hypotheses still to be checked. That is why everything is public and the rules can be corrected."),
            ],
            h_percorso="The path",
            guida_percorso="Four readings in sequence: where we come from, where we are, what does not work, "
                           "what we propose.",
            h_regole="The rules",
            guida_regole="The proposal is written out in full, article by article, so that it can be "
                         "verified and corrected.",
            codici_allegati="{nc} Codes and {na} Technical Annexes", storico="history",
            parametri="Parameters to be verified", parametri_nota="calibration draft",
            h_bozze="Drafts and proposals",
            bozze_sotto="Drafts of the technical annexes that the Codes refer to and that have not yet been "
                        "adopted, and substantive changes under discussion. None is in force.",
            reg_parametri="The proposed numbers, with their origin and the test each would need, are in the "
                          "<a href=\"{par}\">register of parameters to be verified</a>.",
            h_aperto="An open project", h_stato="Status", h_licenza="Licence",
            stato="The project is at the stage of writing and verification. The texts are not a proven "
                  "model: they must be tested, and corrected where they fail.",
            licenza="The rules are free: {lic}. They may be copied, modified and republished, citing the "
                    "source and keeping the same licence. The four texts of the path may be copied and "
                    "republished in full, but not modified: {licp}. Translating them is permitted.",
            contribuire_testo="Read, criticise, verify, correct. Different skills are needed, and concrete "
                              "cases with which to put the rules to the test.",
            desc_home="Born of a refusal of today’s injustices, an open proposal for an alternative to the way we organise collective life: "
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
            attacco="El Proyecto de los Círculos nace del rechazo a las injusticias del mundo de hoy, y propone otra "
                    "manera de vivir juntos. Empieza por la persona, organiza la colectividad y construye los "
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
                ("Por qué", "Porque las injusticias del mundo de hoy no son excepciones, sino el resultado ordinario del modo en que está organizado. Un sistema que mide el valor en beneficio trata el trabajo de las personas y los recursos del planeta como costos que reducir: así la explotación se convierte en la regla, no en el abuso. El poder de usar la fuerza sigue concentrado en los Estados, que lo dirigen contra quien disiente en su interior y contra otros pueblos en las guerras. Y quien ejerce el poder, económico o político, rara vez responde de las consecuencias de sus decisiones. Mientras tanto, el sistema produce mucho, pero no transforma esa riqueza en seguridad, tiempo y libertad de elección para las personas: quien decide, quien gana y quien paga son cada vez más a menudo personas distintas, y el presente se paga trasladando los costos al futuro. Por eso no basta con corregir los efectos: hay que cambiar las condiciones que los producen. De ahí nace este proyecto."),
                ("Qué es", "Un sistema completo para vivir juntos sin que nadie domine a los demás. No es un manifiesto: está escrito por entero, regla por regla, en una Constitución y en los Códigos que la llevan a la práctica, de la vivienda a la justicia, del trabajo a la energía. Puede nacer dentro de la sociedad de hoy, conectando las comunidades solidarias que ya existen sin pedirles que cambien su modo de vivir. Por ahora es una propuesta: no está en vigor en ninguna parte."),
                ("Qué garantiza", "A cada miembro vivienda, alimentos, agua, energía, atención sanitaria, educación y conexión. El pacto es sencillo: quien puede trabaja una parte de lo necesario para todos, y a cambio tiene lo que necesita para vivir. No se recibe en proporción a las horas: los bienes se toman de los Almacenes comunes según la necesidad, y quien no puede trabajar, por edad, enfermedad o discapacidad, recibe lo mismo. Entre los miembros no circula dinero. Lo personal sigue siendo personal."),
                ("Qué pide", "Hacer la propia parte y renunciar a lo que permite dominar a los demás. La propia parte es el trabajo necesario para todos, repartido por turnos entre quienes pueden, para que a cada uno le toque poco. La renuncia afecta a la propiedad privada de la tierra y de los medios de producción, a la acumulación, a las armas y a la explotación de los animales. Quien no esté de acuerdo puede irse cuando quiera."),
                ("Quién decide", "Deciden las personas, directamente, lo más cerca posible de donde viven. Cada decisión se toma en el nivel más pequeño capaz de tomarla: la vida privada sigue siendo de cada cual; lo que concierne a todos se decide juntos, en la propia Comunidad; lo que concierne a varias Comunidades se coordina en círculos más amplios, que coordinan pero no mandan. Cada cual vota por sí mismo, sin delegaciones. No hay jefes ni políticos de oficio: quien coordina es elegido por sorteo entre quienes se ofrecen, por un tiempo limitado, y responde ante quienes le confiaron el encargo."),
                ("Qué no sabemos", "Si funciona: ninguna comunidad la ha probado todavía, y muchas cifras son hipótesis por verificar. Por eso todo es público y las reglas se pueden corregir."),
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
            desc_home="Nacida del rechazo a las injusticias de hoy, una propuesta abierta de alternativa al modo en que organizamos la vida colectiva: "
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
    "fr": dict(
        codice="fr", prefisso="fr/", nome_lingua="Français", regole_da="it",
        nome="Projet des Cercles",
        dir_percorso="parcours", dir_registro="regles", dir_scarica="fr/telechargements",
        pag_modifiche="modifications.html", pag_contribuire="contribuer.html",
        md_modifiche="MODIFICATIONS.md", md_contribuire="CONTRIBUER.md",
        licenza_url="https://creativecommons.org/licenses/by-sa/4.0/deed.fr",
        licenza_percorso_url="https://creativecommons.org/licenses/by-nd/4.0/deed.fr",
        livelli=[("Noyau de soin", "de 1 à 15 personnes", ["soin quotidien", "et hospitalité"]),
                 ("Communauté de base", "30–500 personnes", ["décide en Assemblée,", "gère travail et Entrepôt"]),
                 ("Bassin", "au moins 3 Communautés", ["logistique, hôpital,", "Tribunal de garantie"]),
                 ("Biorégion", "plusieurs Bassins", ["chemins de fer, énergie,", "haute spécialisation"]),
                 ("Cercle global", "l’humanité entière", ["règles communes,", "aucun gouvernement"])],
        ciclo=[("Besoins", ["ce dont les personnes", "ont besoin"]),
               ("Assemblée", ["toutes les personnes,", "une voix chacune"]),
               ("Travail nécessaire", ["par rotation ; en moyenne", "pas plus de 15 heures", "par semaine"]),
               ("Entrepôts communs", ["biens et services", "de tous"]),
               ("Accès", ["à chacun", "selon son besoin"])],
        frecce=["relevés", "décide", "produit", "donnent"],
        maiuscole=["Confédération", "Cercles", "Code", "Annexe", "Assemblée", "Réseau", "Entrepôts communs",
                   "Contribution de base obligatoire", "Solde mondial", "Confédération"],
        t=dict(
            salta="Aller au contenu", sezioni="Sections", percorso="Parcours", registro="Règles",
            contribuire="Contribuer", repository="Dépôt",
            piede="La Constitution, les Codes et les Annexes sont publiés sous licence {lic} : chacun peut les "
                  "copier, les modifier et les republier, en citant la source et en gardant la même licence. Les "
                  "quatre textes du parcours sont publiés sous licence {licp} : ils peuvent être copiés et "
                  "republiés en entier, en citant la source, mais pas modifiés.",
            piede_registro="Ce texte est publié sous licence {lic} : chacun peut le copier, le modifier et le "
                           "republier, en citant la source et en gardant la même licence.",
            piede_percorso="Ce texte est publié sous licence {licp} : chacun peut le copier et le republier en "
                           "entier, en citant la source, mais pas le modifier. Il peut être traduit dans d’autres "
                           "langues, si la traduction est intégrale et fidèle ; pour l’abréger ou l’adapter, il faut "
                           "l’accord des auteurs : voir <a href=\"{con}\">comment contribuer</a>.",
            avviso="Ceci est une traduction de travail. Le texte de référence est l’italien.",
            bozza="Brouillon en cours de vérification : ni adopté, ni mis à l’épreuve",
            modifiche="Registre des modifications", come_contribuire="Comment contribuer",
            capitolo="Chapitre {n} sur {tot} · {min} min de lecture",
            continua="Suite · chapitre {n} sur {tot}",
            fine="Le parcours s’arrête ici", leggi_regole="Lire les règles",
            fine_testo="La Constitution, les seize Codes et les Annexes, avec toutes leurs versions.",
            inizio="← Accueil", capitoli="Chapitres", scarica="Télécharger", indice="Sommaire",
            indice_aria="Sommaire du texte",
            allineamento="Versions des autres textes avec lesquels il est aligné",
            reg_sotto="Tous les textes normatifs du projet, avec leur version. Chaque modification est notée et "
                      "motivée dans le <a href=\"{mod}\">registre des modifications</a>.",
            h_cost="Constitution", h_codici="Codes", h_allegati="Annexes techniques",
            h_come="Comment ils sont organisés",
            come="La Constitution fixe les principes et la structure générale. Les Codes transforment ces principes "
                 "en règles opérationnelles. Les Annexes techniques développent des procédures, des critères et des "
                 "spécifications. En cas de conflit, la Constitution prévaut.",
            desc_reg="Constitution, Codes et Annexes du Projet des Cercles, avec toutes leurs versions.",
            versione="version",
            etichetta="Une proposition ouverte", domanda="Quelles alternatives avons-nous ?",
            attacco="Le Projet des Cercles naît du refus des injustices du monde d’aujourd’hui, et propose une autre "
                    "manière de vivre ensemble. Il part de la personne, organise la collectivité et construit les "
                    "outils pour qu’aucune des deux n’ait à dominer l’autre.",
            comincia="Commencer par le parcours", vai_regole="Aller aux règles", prova_caso="Mettre un cas à l’épreuve",
            h_prova="Mettez-la à l’épreuve",
            guida_prova="Le projet a besoin de critiques plus que d’adhésions. Trois façons de commencer, chacune avec "
                        "des signalements déjà ouverts (pour l’instant en italien ; vous pouvez écrire en français) :",
            prova=[
                ("caso", "Essayer un cas", "Prenez une situation concrète, un conflit ou une objection en Assemblée, "
                                           "et soumettez-la aux procédures : où elles tiennent et où elles cèdent."),
                ("dato", "Vérifier une donnée", "Beaucoup de seuils sont des propositions de départ : de 30 à 500 "
                                                "personnes par Communauté, le quorum, 50 litres d’eau par jour. Il faut "
                                                "des données qui les confirment ou les démentent."),
                ("codice", "Relire un Code", "Si vous connaissez une matière, lisez le Code qui la traite et dites ce "
                                             "qui est faux, ce qui manque, ce qui n’est pas applicable."),
            ],
            senza_conto="Pas de compte GitHub ? Écrivez à {mail} : une ligne suffit.",
            h_minuto="En une minute",
            minuto=[
                ("Pourquoi", "Parce que les injustices du monde d’aujourd’hui ne sont pas des exceptions, mais le résultat ordinaire de la manière dont il est organisé. Un système qui mesure la valeur en profit traite le travail des personnes et les ressources de la planète comme des coûts à réduire : ainsi l’exploitation devient la règle, et non l’abus. Le pouvoir d’user de la force reste concentré entre les mains des États, qui le retournent contre ceux qui contestent à l’intérieur et contre d’autres peuples dans les guerres. Et ceux qui exercent le pouvoir, économique ou politique, répondent rarement des conséquences de leurs décisions. Pendant ce temps, le système produit beaucoup, mais il ne transforme pas cette richesse en sécurité, en temps et en liberté de choix pour les personnes : ceux qui décident, ceux qui gagnent et ceux qui paient sont de plus en plus souvent des personnes différentes, et le présent se paie en reportant les coûts sur l’avenir. C’est pourquoi corriger les effets ne suffit pas : il faut changer les conditions qui les produisent. C’est de là que naît ce projet."),
                ("Ce que c’est", "Un système complet pour vivre ensemble sans que personne ne domine les autres. Ce n’est pas un manifeste : il est écrit dans son intégralité, règle par règle, dans une Constitution et dans les Codes qui la mettent en pratique, du logement à la justice, du travail à l’énergie. Il peut naître au sein de la société d’aujourd’hui, en reliant les communautés solidaires qui existent déjà sans leur demander de changer leur manière de vivre. Pour l’instant, c’est une proposition : elle n’est en vigueur nulle part."),
                ("Ce qu’elle garantit", "À chaque membre, le logement, la nourriture, l’eau, l’énergie, les soins, l’instruction et la connexion. Le pacte est simple : qui le peut fournit une part du travail nécessaire à tous, et reçoit en échange ce dont il a besoin pour vivre. On ne reçoit pas en proportion des heures : les biens se prennent dans les Entrepôts communs selon le besoin, et qui ne peut pas travailler, en raison de l’âge, de la maladie ou du handicap, reçoit autant. Entre les membres, l’argent ne circule pas. Ce qui est personnel reste personnel."),
                ("Ce qu’elle demande", "De faire sa part et de renoncer à ce qui permet de dominer les autres. Sa part, c’est le travail nécessaire à tous, réparti par rotation entre ceux qui le peuvent, pour qu’il en reste peu à chacun. Le renoncement porte sur la propriété privée de la terre et des moyens de production, sur l’accumulation, sur les armes et sur l’exploitation des animaux. Qui n’est pas d’accord peut partir quand il le veut."),
                ("Qui décide", "Ce sont les personnes qui décident, directement, au plus près de là où elles vivent. Chaque décision se prend au plus petit niveau capable de la prendre : la vie privée reste à chacun ; ce qui concerne tout le monde se décide ensemble, dans sa propre Communauté ; ce qui concerne plusieurs Communautés se coordonne dans des cercles plus larges, qui coordonnent mais ne commandent pas. Chacun vote pour soi, sans procuration. Il n’y a ni chefs ni politiciens de métier : ceux qui coordonnent sont tirés au sort parmi les volontaires, pour un temps limité, et rendent compte à ceux qui leur ont confié la tâche."),
                ("Ce que nous ne savons pas", "Si cela fonctionne : aucune communauté ne l’a encore essayé, et beaucoup de chiffres sont des hypothèses à vérifier. C’est pourquoi tout est public et les règles peuvent être corrigées."),
            ],
            h_percorso="Le parcours",
            guida_percorso="Quatre lectures à la suite : d’où nous venons, où nous en sommes, ce qui ne fonctionne pas, "
                           "ce que nous proposons.",
            h_regole="Les règles",
            guida_regole="La proposition est écrite dans son intégralité, article par article, pour pouvoir être "
                         "vérifiée et corrigée.",
            codici_allegati="{nc} Codes et {na} Annexes techniques", storico="historique",
            parametri="Paramètres à vérifier", parametri_nota="brouillon de calibrage",
            h_bozze="Brouillons et propositions",
            bozze_sotto="Brouillons des annexes techniques que les Codes citent et qui ne sont pas encore adoptées, "
                        "et modifications de fond en discussion. Aucun n’est en vigueur.",
            reg_parametri="Les nombres proposés, avec leur origine et la preuve qu’il faudrait pour les confirmer, "
                          "sont dans le <a href=\"{par}\">registre des paramètres à vérifier</a>.",
            h_aperto="Un projet ouvert", h_stato="État", h_licenza="Licence",
            stato="Le projet en est à la phase d’écriture et de vérification. Les textes ne sont pas un modèle "
                  "démontré : ils doivent être mis à l’épreuve, et corrigés là où ils échouent.",
            licenza="Les règles sont libres : {lic}. Elles peuvent être copiées, modifiées et republiées, en citant "
                    "la source et en gardant la même licence. Les quatre textes du parcours peuvent être copiés et "
                    "republiés en entier, mais pas modifiés : {licp}. Les traduire est permis.",
            contribuire_testo="Lire, critiquer, vérifier, corriger. Il faut des compétences diverses et des cas "
                              "concrets pour mettre les règles à l’épreuve.",
            desc_home="Née du refus des injustices d’aujourd’hui, une proposition ouverte d’alternative à la manière dont nous organisons la vie collective : "
                      "le parcours, la Constitution, les Codes.",
            figura="Des personnes disposées en cercle, toutes égales, avec d’autres communautés reliées autour",
            si_uniscono="s’unissent en",
            ritorno="de nouveaux besoins naissent, et le cycle recommence",
            consigli="Conseils techniques et IA", consigli2="proposent et calculent, ne décident pas",
            garanzia="Cercle de garantie", garanzia2="contrôle et reçoit les recours ; charges brèves, tirées au sort",
            did_livelli="Les cinq niveaux, de la personne à la planète. Aucun niveau ne commande celui du dessous : "
                        "chaque décision reste au niveau le plus proche qui peut la prendre.",
            did_ciclo="Comment fonctionne une Communauté : on part des besoins, l’Assemblée décide, le travail "
                      "nécessaire remplit les Entrepôts et chacun y accède selon son besoin.",
        ),
    ),
}


# ----------------------------------------------------------------- lettura

def ha_registro(lingua):
    """Vero se la lingua ha i propri testi normativi (Costituzione, Codici, Allegati)."""
    return bool(glob.glob(os.path.join(TESTI, lingua["codice"], lingua["dir_registro"], "*.md")))


def ha_domande(lingua):
    """Vero se la lingua ha il proprio file di domande frequenti."""
    return os.path.exists(os.path.join(RADICE, ricerca.LINGUE[lingua["codice"]]["md"]))


def lingua_regole(lingua):
    """La lingua in cui si leggono le regole: la propria, oppure quella indicata in «regole_da»."""
    return lingua if ha_registro(lingua) else LINGUE[lingua["regole_da"]]


def lingua_servizio(lingua):
    """La lingua delle pagine di bozze e parametri: la propria, se tradotte, altrimenti l'italiano."""
    return lingua if lingua["codice"] in PARAMETRI else LINGUE["it"]


def url_parametri(lingua, profondita=0):
    """Indirizzo del registro dei parametri, visto da una pagina della lingua a una certa profondità."""
    lp = lingua_servizio(lingua)
    su = "../" * (lingua["prefisso"].count("/") + profondita)
    return "%s%s%s/%s" % (su, lp["prefisso"], lp["dir_registro"], PARAMETRI[lp["codice"]]["pagina"])


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


COMMA_AGG = re.compile(r"<p>(\d+-(?:bis|ter|quater|quinquies|sexies)\.)\s")
LETTERA = re.compile(r"<p>[a-z]\) ")


def commi_aggiunti(corpo):
    """Nei Codici, i commi inseriti dopo (1-bis, 3-ter...) sono paragrafi fuori dalla lista numerata:
    li allineo al testo dei commi e ne segno il numero come quello della lista. Le lettere che li
    seguono restano allo stesso margine."""
    pezzi = re.split(r"(?=<p>)", corpo)
    fuori, dentro = [], False
    for pezzo in pezzi:
        m = COMMA_AGG.match(pezzo)
        if m:
            pezzo = '<p class="comma-agg"><span class="num-agg">%s</span> ' % m.group(1) + pezzo[m.end():]
            dentro = True
        elif dentro and LETTERA.match(pezzo):
            pezzo = '<p class="comma-agg">' + pezzo[3:]
        else:
            dentro = False
        fuori.append(pezzo)
    return "".join(fuori)


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
    testo = re.sub(r"\b(Allegato tecnico|Technical annex|Annexe technique) ([abc])\b",
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

    # le lingue senza la pagina corrispondente rimandano alla loro pagina iniziale: non sono vere alternative
    vere = {c: i for c, i in (gemelle or {}).items()}
    if not all(i.endswith("index.html") for i in vere.values()):
        vere = {c: i for c, i in vere.items() if not i.endswith("/index.html") or "/" in i.split("/", 1)[-1]}
    alternative = "".join('\n<link rel="alternate" hreflang="%s" href="%s/%s">' % (c, SITO_URL, indirizzo)
                          for c, indirizzo in vere.items()) if SITO_URL else ""
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
<link rel="icon" href="%(base)sassets/icona.svg" type="image/svg+xml">%(anteprima)s%(alternative)s
</head>
<body>
<a class="salta" href="#contenuto">%(salta)s</a>
<header class="testata">
  <a class="marchio" href="%(radice)sindex.html">%(logo)s<span>%(nome)s</span></a>
  <nav aria-label="%(sezioni)s">%(v1)s%(v2)s%(v4)s%(v3)s%(cambio)s</nav>
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
           salta=t["salta"], sezioni=t["sezioni"], cambio=cambio, avviso=avviso, alternative=alternative,
           piede=piede, reg=dir_regole(lingua), pmod=lingua_regole(lingua)["pag_modifiche"],
           pcon=lingua["pag_contribuire"], modifiche=t["modifiche"], come=t["come_contribuire"],
           deposito=deposito,
           v1=voce(t["percorso"], "index.html#percorso", "percorso"),
           v2=voce(t["registro"], dir_regole(lingua) + "/index.html", "registro"),
           v3=voce(t["contribuire"], lingua["pag_contribuire"], "contribuire"),
           v4=voce(ricerca.LINGUE[lingua["codice"]]["voce"], ricerca.LINGUE[lingua["codice"]]["pagina"], "domande")
           if ha_domande(lingua) else "")


# nomi con cui il progetto viene cercato: finiscono nei dati strutturati delle pagine iniziali
NOMI_SITO = {
    "it": ["Confederazione dei Cerchi", "Costituzione della Confederazione dei Cerchi"],
    "en": ["Confederation of Circles", "Progetto dei Cerchi", "Confederazione dei Cerchi"],
    "fr": ["Confédération des Cercles", "Progetto dei Cerchi", "Confederazione dei Cerchi"],
    "es": ["Confederación de los Círculos", "Progetto dei Cerchi", "Confederazione dei Cerchi"],
}
ALTERNATIVA = re.compile(r'\n?<link rel="alternate" hreflang="([\w-]+)" href="([^"]+)">')


def indirizzo_pubblico(indirizzo):
    """Un solo indirizzo per pagina: la cartella, non la cartella seguita da index.html."""
    return re.sub(r"(^|/)index\.html$", r"\1", indirizzo)


def rifinisci(lingua, relativo, contenuto):
    """Aggiunge all'intestazione l'indirizzo canonico, le lingue complete e, nelle pagine iniziali,
    il nome del sito per i motori di ricerca."""
    if not SITO_URL or not relativo.endswith(".html") or "</head>" not in contenuto:
        return contenuto
    proprio = indirizzo_pubblico("%s/%s%s" % (SITO_URL, lingua["prefisso"], relativo))
    gemelle = {c: indirizzo_pubblico(i) for c, i in ALTERNATIVA.findall(contenuto)}
    if relativo != "index.html":   # una pagina iniziale non è la traduzione di una pagina interna
        gemelle = {c: i for c, i in gemelle.items()
                   if c not in LINGUE or i != "%s/%s" % (SITO_URL, LINGUE[c]["prefisso"])}
    contenuto = ALTERNATIVA.sub("", contenuto)
    righe = ['<link rel="canonical" href="%s">' % html.escape(proprio),
             '<meta property="og:url" content="%s">' % html.escape(proprio)]
    if gemelle:
        gemelle[lingua["codice"]] = proprio
        ordine = sorted(gemelle, key=lambda c: list(LINGUE).index(c) if c in LINGUE else len(LINGUE))
        righe += ['<link rel="alternate" hreflang="%s" href="%s">' % (c, html.escape(gemelle[c])) for c in ordine]
        if "it" in gemelle:
            righe.append('<link rel="alternate" hreflang="x-default" href="%s">' % html.escape(gemelle["it"]))
    if relativo == "index.html":
        dati = {"@context": "https://schema.org", "@type": "WebSite", "name": lingua["nome"],
                "alternateName": NOMI_SITO.get(lingua["codice"], []), "url": proprio,
                "inLanguage": lingua["codice"]}
        righe.append('<script type="application/ld+json">%s</script>'
                     % json.dumps(dati, ensure_ascii=False).replace("</", "<\\/"))
    return contenuto.replace("</head>", "\n".join(righe) + "\n</head>", 1)


def scrivi(lingua, relativo, contenuto):
    destinazione = os.path.join(SITO_DIR, lingua["prefisso"], relativo)
    os.makedirs(os.path.dirname(destinazione), exist_ok=True)
    open(destinazione, "w", encoding="utf-8").write(rifinisci(lingua, relativo, contenuto))


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
    documenti = []                               # per la ricerca: (titolo, indirizzo, unità)
    ancore = ANCORE.setdefault(lingua["codice"], {})

    def indicizza(titolo, indirizzo, markdown, corpo, cost=False, peso=1.0):
        try:
            documenti.append((titolo, indirizzo, ricerca.unita(markdown, corpo, cost), peso))
        except ValueError as errore:
            print("  ricerca: %s non indicizzato (%s)" % (indirizzo, errore))

    # --- capitoli del percorso
    for i, (meta, testo) in enumerate(percorso):
        _, corpo = pandoc(testo)
        indicizza(meta["titolo"], "%s/%s.html" % (dp, meta["slug"]), testo, corpo, peso=0.7)
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
        cost = meta["gruppo"] == "costituzione"
        if cost:
            corpo = ricerca.ancore_commi(corpo)
        else:
            corpo = commi_aggiunti(corpo)
        articoli, commi = ricerca.ancore_articoli(corpo)
        ancore[meta["id"]] = dict(slug=meta["slug"], articoli=articoli, commi=commi, costituzione=cost)
        indicizza(meta["breve"], "%s/%s.html" % (dr, meta["slug"]), abbassa_titoli(testo), corpo, cost,
                  1.2 if cost else 1.0)
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
                      DESC_REGOLA.get(lingua["codice"], DESC_REGOLA["it"]).format(breve=meta["breve"], v=meta["versione"]),
                      contenuto, 1, "registro", gemelle(meta["id"])))

    # --- indice del registro
    base_bozze = url_parametri(lingua, 1).rsplit("/", 1)[0]
    bozze = '<h2>%s</h2>\n<p>%s</p>\n<ul class="testi">%s</ul>' % (
        t["h_bozze"], t["bozze_sotto"],
        "\n".join('<li><a href="%s/%s">%s</a><span class="versione">%s</span></li>'
                  % (base_bozze, b["pagina"], html.escape(b["titolo"]), b["nota"])
                  for b in BOZZE[lingua_servizio(lingua)["codice"]]))

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
    if lingua["codice"] in PARAMETRI:
        def gemelle_servizio(chiave):
            esito = {}
            for a in altre:
                la = lingua_servizio(a)
                if chiave == "parametri":
                    pag = PARAMETRI[la["codice"]]["pagina"]
                else:
                    pag = next((b["pagina"] for b in BOZZE[la["codice"]] if b["chiave"] == chiave), None)
                    if pag is None:
                        continue
                esito[a["codice"]] = "%s%s/%s" % (la["prefisso"], la["dir_registro"], pag)
            return esito
        par = PARAMETRI[lingua["codice"]]
        servizio.append((par["md"], "%s/%s" % (dr, par["pagina"]), t["parametri"], 1, "registro",
                         gemelle_servizio("parametri"), " largo"))
        for b in BOZZE[lingua["codice"]]:
            servizio.append((b["md"], "%s/%s" % (dr, b["pagina"]), b["titolo"], 1, "registro",
                             gemelle_servizio(b["chiave"]), b.get("classe", " largo")))
    if proprie:
        servizio.append(
            (lingua["md_modifiche"], "%s/%s" % (dr, lingua["pag_modifiche"]), t["modifiche"], 1, "registro",
             dict((a["codice"], "%s%s/%s" % (a["prefisso"], a["dir_registro"], a["pag_modifiche"]))
                  for a in altre if ha_registro(a)), ""))
    for origine, destinazione, titolo, profondita, sezione, gem, classe in servizio:
        testo = open(os.path.join(RADICE, origine), encoding="utf-8").read()
        testo = re.sub(r"\A# .*\n", "", testo)
        _, corpo = pandoc(abbassa_titoli(testo))
        indicizza(titolo, destinazione, abbassa_titoli(testo), corpo,
                  peso=0.85 if sezione == "contribuire" else 0.6)        # bozze, proposte, parametri: dopo le regole
        contenuto = ('<article class="foglio%s"><header class="apertura"><h1>%s</h1></header>'
                     '<div class="prosa">%s</div></article>' % (classe, titolo, corpo))
        scrivi(lingua, destinazione,
               pagina(lingua, "%s — %s" % (titolo, nome), titolo + ".", contenuto, profondita, sezione, gemelle("", gem)))

    # --- domande frequenti e ricerca nei testi
    cerca_home = ""
    if ha_domande(lingua):
        rl = ricerca.LINGUE[lingua["codice"]]
        base_assets = "../" * lingua["prefisso"].count("/")
        titolo_d, premessa, gruppi = ricerca.leggi_domande(os.path.join(RADICE, rl["md"]),
                                                           ANCORE[lreg["codice"]], dr)
        scrivi(lingua, rl["pagina"],
               pagina(lingua, "%s — %s" % (titolo_d, nome), rl["descrizione"],
                      ricerca.pagina_domande(lingua["codice"], titolo_d, premessa, gruppi, base_assets,
                                             lingua["pag_contribuire"]),
                      0, "domande",
                      gemelle("", dict((a["codice"], "%s%s" % (a["prefisso"], ricerca.LINGUE[a["codice"]]["pagina"]))
                                       for a in altre if ha_domande(a)))))
        os.makedirs(os.path.join(SITO_DIR, "assets"), exist_ok=True)
        open(os.path.join(SITO_DIR, "assets", "indice-%s.js" % lingua["codice"]), "w", encoding="utf-8").write(
            ricerca.indice_js(lingua["codice"], documenti, gruppi, lingua["pag_contribuire"]))
        cerca_home = ricerca.modulo_home(lingua["codice"])

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
  %(cerca_home)s
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
        etichetta=t["etichetta"], domanda=t["domanda"], attacco=t["attacco"], dp=dp, dr=dr, cerca_home=cerca_home,
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
           pagina(lingua, TITOLO_HOME.get(lingua["codice"], nome), t["desc_home"], contenuto, 0, "", gemelle()))


def costruisci():
    presenti = [c for c in LINGUE if os.path.isdir(os.path.join(TESTI, c))]
    for codice in presenti:
        costruisci_lingua(LINGUE[codice], [LINGUE[c] for c in presenti if c != codice])
    # foglio di stile e file che evita l'elaborazione Jekyll su alcuni servizi
    os.makedirs(os.path.join(SITO_DIR, "assets"), exist_ok=True)
    shutil.copy(os.path.join(RADICE, "strumenti", "stile.css"), os.path.join(SITO_DIR, "assets", "stile.css"))
    shutil.copy(os.path.join(RADICE, "strumenti", "cerca.js"), os.path.join(SITO_DIR, "assets", "cerca.js"))
    open(os.path.join(SITO_DIR, "assets", "icona.svg"), "w", encoding="utf-8").write(icona())
    anteprima = os.path.join(RADICE, "immagini", "copertina.png")
    if os.path.exists(anteprima):
        shutil.copy(anteprima, os.path.join(SITO_DIR, "assets", "copertina.png"))
    open(os.path.join(SITO_DIR, ".nojekyll"), "w").close()
    if SITO_URL:
        indirizzi = []
        for cartella, _, nomi in os.walk(SITO_DIR):
            for n in sorted(nomi):
                if n.endswith(".html") and not n.startswith("google"):   # i file di verifica di Google non sono pagine
                    rel = os.path.relpath(os.path.join(cartella, n), SITO_DIR).replace(os.sep, "/")
                    indirizzi.append(SITO_URL + "/" + (rel[:-10] if rel.endswith("index.html") else rel))
        with open(os.path.join(SITO_DIR, "sitemap.xml"), "w", encoding="utf-8") as m:
            m.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
            m.write("".join("  <url><loc>%s</loc></url>\n" % html.escape(u) for u in sorted(indirizzi)))
            m.write("</urlset>\n")
    print("Sito costruito in", SITO_DIR, "— lingue:", ", ".join(presenti))


if __name__ == "__main__":
    if shutil.which("pandoc") is None:
        sys.exit("Serve pandoc: https://pandoc.org/installing.html")
    costruisci()
