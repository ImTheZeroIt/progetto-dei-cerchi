#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Primo bilancio delle ore di una Comunità tipo.

Rifà i conti della bozza dell'Allegato Tecnico UCR (bozze/allegato-ucr.md).
Ogni numero è un'ipotesi dichiarata: per provarne un'altra basta cambiarla qui sotto e rieseguire

    python3 strumenti/bilancio_ore.py

Le fonti di ogni valore sono elencate nella bozza. Dove non c'è una fonte, il valore è segnato «ipotesi».
"""

# ------------------------------------------------------------------ popolazione
PERSONE = 150

# Struttura per età dell'UE al 1° gennaio 2024 (Eurostat, demo_pjanind), in percentuale
ETA = {"0-17": 17.8, "70-74": 5.3, "75+": 10.2}
ETA["18-69"] = 100 - sum(ETA.values())
SOTTO_3 = 2.57           # bambini sotto i tre anni, % della popolazione (Eurostat, demo_pjan)
SOTTO_1 = 0.806          # nati nell'anno, % della popolazione (Eurostat, demo_pjan)
GENITORI_PER_BAMBINO = 1.8    # ipotesi: qualche bambino ha fratelli sotto i tre anni o un solo genitore
ALTRE_RIDUZIONI = 0.05   # ipotesi: disabilità grave, caregiver, malattia (Cod. 1, art. 11)

LIMITE_ORE = 15          # Cod. 1, art. 3
SETTIMANE = 52

# ------------------------------------------------------------------ economia esterna (UE, 2024)
ORE_UE = 353_652.743e6   # ore lavorate nell'UE (Eurostat, nama_10_a10_e)
ABITANTI_UE = 449_306_184
PIL_UE = 18_043_409.9e6  # euro correnti (Eurostat, nama_10_gdp)
OCCUPATI_UE = 219_422.70e3
QUOTE_ORE = {            # % delle ore lavorate nell'UE (Eurostat, nama_10_a10_e e nama_10_a64_e)
    "agricoltura": 4.6, "industria alimentare": 2.26, "ristorazione e alloggio": 5.12,
    "manifattura": 14.3, "energia, acqua, rifiuti": 1.42, "costruzioni": 7.5,
    "trasporti e magazzini": 5.59, "sanità": 5.80, "assistenza sociale": 3.82, "istruzione": 5.74,
}

# ------------------------------------------------------------------ Paniere Alimentare (bozza del Paniere)
GRAMMI = {"cereali": 275, "legumi": 100, "frutta secca": 75, "ortaggi": 300, "frutta": 200,
          "tuberi": 50, "olio": 40}
PERDITE = 0.15           # ipotesi: perdite, scarti e semente
DIVARIO_BIO = 0.20       # rese senza chimica di sintesi: -19,2% (Ponisio e altri, 2015)
RESA = {                 # t/ha, Italia 2024 (FAO, da Our World in Data)
    "cereali": 3.66, "legumi": 2.08, "tuberi": 28.78, "ortaggi": 32.17, "frutta": 15.45,
    "frutta secca": 1.33 * 0.47,     # nocciole in guscio per resa in sgusciato (46-48%)
    "olio": 2.61 * 0.40,             # girasole per resa in olio (circa 40%)
}
ORE_ETTARO = {           # ore per ettaro all'anno: valori centrali delle tabelle regionali italiane
    "cereali": 45, "legumi": 80, "tuberi": 300, "ortaggi": 700, "frutta": 530,
    "frutta secca": 300, "olio": 35,
}
ORE_TRASFORMAZIONE = 1800    # ipotesi: mulino 230, forno 640 (metà dei cereali in pane), frantoio e conserve 930
PASTI_AL_GIORNO = 1          # ipotesi: un pasto collettivo per persona al giorno
PASTI_PER_ORA = 12           # cucine convenzionali piccole: da 8 a 18 pasti per ora di lavoro

# ------------------------------------------------------------------ altre voci
FATTORE_PICCOLA_SCALA = 2    # ipotesi: energia e acqua costano il doppio delle ore della media UE
SANITARI_PER_1000 = 4.45     # soglia OMS: medici, infermieri, ostetriche
ADDETTI_CURA_PER_100_ANZIANI = 5     # media OCSE
ANZIANI = 21.6               # % di popolazione con 65 anni o più
ORE_NIDO = 40 * 48           # ipotesi: 40 ore a settimana per 48 settimane, un adulto ogni cinque bambini
ALUNNI_PER_INSEGNANTE = 12.2 # UE, primaria e secondaria (Eurostat)
QUOTA_MANUTENZIONE = 0.5     # ipotesi: metà delle ore delle costruzioni è manutenzione
ORE_LOGISTICA = (6 + 1) * 365        # ipotesi: un turno di 6 ore al Magazzino e un'ora di consegne al giorno
BUCATO_KG = 80               # per persona all'anno (Millward-Hopkins e altri, 2020)
BUCATO_KG_ORA = 25           # lavanderie piccole: 19-26 kg per ora di lavoro
ORE_PULIZIE = 2 * 365        # ipotesi: spazi comuni
ORE_RETE = 8 * 52            # ipotesi
ORE_SANTUARI = 10 * 52       # ipotesi: santuari animali e riparazione ambientale
QUOTA_CIVICA = 0.10          # tetto: Cod. 3, art. 12-bis, c. 13

# ------------------------------------------------------------------ manufatti, contati sul bisogno
# Ogni riga: gruppo, voce, prezzo in euro, anni di durata, persone che condividono il bene.
# Prezzi e durate sono ipotesi di redazione: vanno sostituiti con preventivi e misure reali.
# Il costo annuo per persona è prezzo / durata / persone; le ore sono euro per il coefficiente ore per euro.
MANUFATTI = [
    ("Persona e Nucleo", "vestiario e calzature: 4 kg l'anno a 50 euro al kg", 200, 1, 1),
    ("Persona e Nucleo", "letto e materasso", 500, 15, 1),
    ("Persona e Nucleo", "arredi: tavolo, sedie, contenitori", 600, 25, 1),
    ("Persona e Nucleo", "biancheria, stoviglie, pentole", 300, 10, 1),
    ("Persona e Nucleo", "frigorifero con congelatore", 600, 15, 3),
    ("Persona e Nucleo", "piano di cottura e forno", 500, 15, 3),
    ("Persona e Nucleo", "lavatrice in lavanderia comune", 1500, 12, 15),
    ("Persona e Nucleo", "telefono", 250, 6, 1),
    ("Persona e Nucleo", "computer del Nucleo", 600, 7, 3),
    ("Persona e Nucleo", "Nodo-IA personale", 400, 8, 1),
    ("Persona e Nucleo", "bicicletta e ricambi", 800, 15, 1),
    ("Persona e Nucleo", "prodotti per l'igiene", 120, 1, 1),
    ("Persona e Nucleo", "lampade, piccoli apparecchi, attrezzi domestici", 400, 10, 1),
    ("Salute", "farmaci e materiale sanitario", 300, 1, 1),
    ("Salute", "attrezzature sanitarie del Bacino", 1500, 15, 1),
    ("Abitare", "materiali per abitazioni: 15 m2 a 750 euro di materiali al m2", 11250, 80, 1),
    ("Abitare", "materiali per edifici comuni: 5 m2 a persona", 3750, 80, 1),
    ("Energia e acqua", "fotovoltaico: 2 kW a persona", 2400, 25, 1),
    ("Energia e acqua", "accumulo", 500, 12, 1),
    ("Energia e acqua", "calore: pompe di calore, solare termico", 1500, 18, 1),
    ("Energia e acqua", "rete idrica, pompe, depurazione", 1000, 40, 1),
    ("Energia e acqua", "ricambi e materiali di consumo", 35, 1, 1),
    ("Produzione", "macchine agricole, irrigazione, mulino, frantoio, celle", 250000, 20, 150),
    ("Produzione", "sementi, materiali ed energia per i campi", 60, 1, 1),
    ("Produzione", "cucina collettiva e Magazzino", 100000, 15, 150),
    ("Produzione", "officina e attrezzi comuni", 80000, 15, 150),
    ("Produzione", "materiali di consumo dell'officina", 30, 1, 1),
    ("Mobilità e Rete", "tre mezzi elettrici leggeri e cargo bike", 100000, 12, 150),
    ("Mobilità e Rete", "trasporto pubblico: 3.000 km l'anno a 10 centesimi", 300, 1, 1),
    ("Mobilità e Rete", "server, apparati e cavi della Rete", 60000, 8, 150),
    ("Mobilità e Rete", "collegamento alla rete esterna", 60, 1, 1),
    ("Apprendimento", "materiali e strumenti", 50, 1, 1),
]
FATTORE_ORE_IMPORTATE = 2    # ipotesi: i beni prodotti dove il lavoro rende meno contengono il doppio delle ore


def conto():
    r = {}
    # --- chi contribuisce
    adulti = PERSONE * ETA["18-69"] / 100
    settantenni = PERSONE * ETA["70-74"] / 100 * 0.5
    puerpere = PERSONE * SOTTO_1 / 100
    genitori = PERSONE * SOTTO_3 / 100 * GENITORI_PER_BAMBINO - puerpere
    piene = adulti + settantenni - puerpere - genitori * 0.5
    piene -= (adulti + settantenni) * ALTRE_RIDUZIONI
    r["contributori"] = piene
    r["disponibili"] = piene * LIMITE_ORE * SETTIMANE
    # --- economia esterna
    r["ore_abitante_ue"] = ORE_UE / ABITANTI_UE
    r["ore_per_euro"] = ORE_UE / PIL_UE
    r["ore_annue_occupato"] = ORE_UE / OCCUPATI_UE
    ue = lambda voce: r["ore_abitante_ue"] * QUOTE_ORE[voce] / 100 * PERSONE
    # --- campo
    campo, ettari = {}, {}
    for voce, g in GRAMMI.items():
        tonnellate = g * 365 * PERSONE / 1e6 * (1 + PERDITE)
        ettari[voce] = tonnellate / (RESA[voce] * (1 - DIVARIO_BIO))
        campo[voce] = ettari[voce] * ORE_ETTARO[voce]
    r["ettari"], r["campo"] = ettari, campo
    pasti = PERSONE * 365 * PASTI_AL_GIORNO / PASTI_PER_ORA
    alimentazione = sum(campo.values()) + ORE_TRASFORMAZIONE + pasti
    r["pasti"] = pasti
    # --- voci comuni ai due scenari
    energia = ue("energia, acqua, rifiuti") * FATTORE_PICCOLA_SCALA
    altre = PERSONE * BUCATO_KG / BUCATO_KG_ORA + ORE_PULIZIE + ORE_RETE + ORE_SANTUARI
    annue = r["ore_annue_occupato"]
    minori_3_17 = PERSONE * (ETA["0-17"] - SOTTO_3) / 100
    # --- scenario A: standard minimi
    a = {
        "Alimentazione": alimentazione,
        "Energia e acqua": energia,
        "Cura: sanità": PERSONE * SANITARI_PER_1000 / 1000 * annue,
        "Cura: anziani e persone non autosufficienti":
            PERSONE * ANZIANI / 100 * ADDETTI_CURA_PER_100_ANZIANI / 100 * annue,
        "Cura: nido": ORE_NIDO,
        "Apprendimento dei minori": minori_3_17 / ALUNNI_PER_INSEGNANTE * annue,
        "Manutenzione": ue("costruzioni") * QUOTA_MANUTENZIONE,
        "Logistica": ORE_LOGISTICA,
        "Altre attività": altre,
    }
    # --- scenario B: servizi al livello dell'UE di oggi
    b = dict(a)
    b["Cura: sanità"] = ue("sanità")
    b["Cura: anziani e persone non autosufficienti"] = ue("assistenza sociale")
    b["Cura: nido"] = 0.0          # già compreso nell'assistenza sociale
    b["Apprendimento dei minori"] = ue("istruzione")
    b["Manutenzione"] = ue("costruzioni")
    for s in (a, b):
        s["Funzioni civiche e documentazione"] = sum(s.values()) / (1 - QUOTA_CIVICA) * QUOTA_CIVICA
    r["A"], r["B"] = a, b
    r["manifattura_ue"] = ue("manifattura") - ue("industria alimentare")   # il cibo è già contato sopra
    r["cibo_ue"] = ue("agricoltura") + ue("industria alimentare") + ue("ristorazione e alloggio")
    r["casa_nel_cbo"] = (pasti + ORE_NIDO + PERSONE * BUCATO_KG / BUCATO_KG_ORA + ORE_PULIZIE) / (1 - QUOTA_CIVICA)
    # --- manufatti contati sul bisogno
    gruppi = {}
    for gruppo, _, euro, anni, persone in MANUFATTI:
        gruppi[gruppo] = gruppi.get(gruppo, 0) + euro / anni / persone
    r["manufatti_euro"] = gruppi                                   # euro per persona all'anno
    r["manufatti_ore"] = sum(gruppi.values()) * r["ore_per_euro"] * PERSONE
    return r


def stampa():
    r = conto()
    n = lambda x: ("%d" % round(x)).rjust(7)
    print("Comunità di %d persone" % PERSONE)
    print("Contributori equivalenti: %.1f (%.0f%% della popolazione)" % (r["contributori"], 100 * r["contributori"] / PERSONE))
    print("Ore disponibili all'anno: %s  (%.0f per abitante)" % (n(r["disponibili"]), r["disponibili"] / PERSONE))
    print("\nTerra per il Paniere Alimentare")
    for v in r["ettari"]:
        print("  %-14s %5.2f ha  %s ore" % (v, r["ettari"][v], n(r["campo"][v])))
    print("  %-14s %5.2f ha  %s ore" % ("totale", sum(r["ettari"].values()), n(sum(r["campo"].values()))))
    print("  trasformazione %s ore; pasti collettivi %s ore" % (n(ORE_TRASFORMAZIONE), n(r["pasti"])))
    print("\n%-46s %9s %9s" % ("Ore necessarie all'anno", "A", "B"))
    for v in r["A"]:
        print("%-46s %9s %9s" % (v, n(r["A"][v]), n(r["B"][v])))
    for nome, s in (("A", r["A"]), ("B", r["B"])):
        tot = sum(s.values())
        print("Scenario %s: %s ore = %.0f%% delle disponibili = %.1f ore a settimana per contributore"
              % (nome, n(tot), 100 * tot / r["disponibili"], tot / r["contributori"] / SETTIMANE))
    print("\nEconomia esterna (UE, 2024)")
    print("  ore lavorate per abitante all'anno: %.0f" % r["ore_abitante_ue"])
    print("  ore annue per occupato: %.0f" % r["ore_annue_occupato"])
    print("  prodotto per abitante: %.0f euro" % (PIL_UE / ABITANTI_UE))
    print("  ore di lavoro per euro di prodotto: %.4f (1 ora = %.0f euro)" % (r["ore_per_euro"], 1 / r["ore_per_euro"]))
    print("  ore disponibili su ore lavorate nell'UE, per abitante: %.0f%%"
          % (100 * r["disponibili"] / PERSONE / r["ore_abitante_ue"]))
    print("  manifattura senza industria alimentare, per %d persone: %s ore" % (PERSONE, n(r["manifattura_ue"])))
    print("  agricoltura, industria alimentare e ristorazione, per %d persone: %s ore" % (PERSONE, n(r["cibo_ue"])))
    print("\nManufatti contati sul bisogno (euro per persona all'anno)")
    for g, e in r["manufatti_euro"].items():
        print("  %-18s %6.0f euro  %s ore per %d persone" % (g, e, n(e * r["ore_per_euro"] * PERSONE), PERSONE))
    tot_e = sum(r["manufatti_euro"].values())
    ore_m = r["manufatti_ore"]
    sett0 = lambda ore: ore / r["contributori"] / SETTIMANE
    print("  %-18s %6.0f euro  %s ore = %.1f ore a settimana per contributore" % ("totale", tot_e, n(ore_m), sett0(ore_m)))
    print("  con il fattore %d per i beni importati: %s ore = %.1f ore a settimana"
          % (FATTORE_ORE_IMPORTATE, n(ore_m * FATTORE_ORE_IMPORTATE), sett0(ore_m * FATTORE_ORE_IMPORTATE)))
    print("\nConto completo: lavoro interno più manufatti (ore a settimana per contributore)")
    for nome in ("A", "B"):
        interno = sum(r[nome].values())
        print("  scenario %s: %.1f + %.1f = %.1f  (con il fattore %d: %.1f); margine %.1f - %.1f ore"
              % (nome, sett0(interno), sett0(ore_m), sett0(interno + ore_m), FATTORE_ORE_IMPORTATE,
                 sett0(interno + ore_m * FATTORE_ORE_IMPORTATE),
                 LIMITE_ORE - sett0(interno + ore_m * FATTORE_ORE_IMPORTATE), LIMITE_ORE - sett0(interno + ore_m)))
    print("  inventario triplicato: A %.1f, B %.1f" % (sett0(sum(r["A"].values()) + 3 * ore_m), sett0(sum(r["B"].values()) + 3 * ore_m)))
    print("  1.000 euro di acquisti per persona all'anno = %.1f ore a settimana per contributore"
          % sett0(1000 * r["ore_per_euro"] * PERSONE))
    print("  scenario B: %.0f%% delle ore lavorate oggi nell'UE per abitante"
          % (100 * sum(r["B"].values()) / PERSONE / r["ore_abitante_ue"]))
    # stima indipendente: McElroy e O'Neill (2025), Regno Unito
    print("\nStima indipendente (McElroy e O'Neill, 2025), riportata in ore di CBO")
    quota_15_64 = 0.638
    for nome, ore in (("solo beni indispensabili", 17.5), ("minimo realistico secondo gli autori", 36.7),
                      ("buona vita", 45.5), ("Regno Unito oggi", 64.7)):
        per_abitante = ore * 46.6 * 0.8 * quota_15_64
        print("  %s: %.0f ore per abitante all'anno = %.1f ore di CBO a settimana"
              % (nome, per_abitante, per_abitante * PERSONE / r["contributori"] / SETTIMANE))
    casa = r["casa_nel_cbo"]
    print("  lavoro di casa portato nel CBO (pasti, nido, lavanderia, pulizie): %s ore = %.1f ore a settimana"
          % (n(casa), casa / r["contributori"] / SETTIMANE))
    print("\nSe cambia un'ipotesi (scenario A: %.1f ore a settimana)" % (sum(r["A"].values()) / r["contributori"] / SETTIMANE))
    tot_a = sum(r["A"].values())
    lordo = lambda ore: ore / (1 - QUOTA_CIVICA)
    sett = lambda ore: ore / r["contributori"] / SETTIMANE
    casi = [("tre pasti collettivi al giorno", lordo(2 * r["pasti"])),
            ("nessun pasto collettivo", lordo(-r["pasti"])),
            ("frutta secca dimezzata, senza sostituto", lordo(-r["campo"]["frutta secca"] / 2)),
            ("cereali, legumi e girasole a 8 ore per ettaro",
             lordo(-sum(r["campo"][v] - r["ettari"][v] * 8 for v in ("cereali", "legumi", "olio")))),
            ("energia e acqua alla media UE", lordo(-r["A"]["Energia e acqua"] / 2))]
    for nome, delta in casi:
        print("  %-48s %+7d ore -> %.1f ore a settimana" % (nome, round(delta), sett(tot_a + delta)))
    disp48 = r["contributori"] * LIMITE_ORE * 48
    print("  48 settimane di lavoro invece di 52: ore disponibili %s; A %.0f%%, B %.0f%%"
          % (n(disp48), 100 * tot_a / disp48, 100 * sum(r["B"].values()) / disp48))
    tutto = 3 * 365 * PERSONE
    print("  tutto il lavoro di casa di oggi (3 ore al giorno a persona): %s ore = %.0f ore a settimana per contributore"
          % (n(tutto), sett(tutto)))
    ore_persona = LIMITE_ORE * SETTIMANE
    print("\nIl limite è individuale: persone abilitate necessarie a %d ore l'anno ciascuna" % ore_persona)
    for nome in ("A", "B"):
        print("  scenario %s: sanità %.1f; apprendimento dei minori %.1f"
              % (nome, r[nome]["Cura: sanità"] / ore_persona, r[nome]["Apprendimento dei minori"] / ore_persona))
    print("  cinquecento UCR = %.0f euro = %.2f%% delle ore annue; 2.500 UCR = %.0f euro = %.2f%%"
          % (500 / r["ore_per_euro"], 100 * 500 / r["disponibili"], 2500 / r["ore_per_euro"], 100 * 2500 / r["disponibili"]))


def esempio_pane():
    """Esempio svolto della bozza: UCR di un chilo di pane. I valori segnati «esempio» non sono misure."""
    r = conto()
    h_euro = r["ore_per_euro"]
    resa = RESA["cereali"] * (1 - DIVARIO_BIO) * 1000            # kg di grano per ettaro
    campo = (ORE_ETTARO["cereali"] + 400 * h_euro) / resa        # esempio: 400 euro di acquisti e macchine per ettaro
    kwh = 0.25 * h_euro                                          # esempio: elettricità acquistata a 0,25 euro per kWh
    mulino = 15 / 1000 + 0.05 * kwh + 0.02 * h_euro              # esempio: 15 ore per tonnellata, 0,05 kWh e 2 centesimi per kg
    farina = (campo + mulino) / 0.95                             # esempio: 95 kg di farina integrale da 100 kg di grano
    voci = [("farina (0,74 kg)", farina / 1.35),                 # esempio: 1,35 kg di pane da 1 kg di farina
            ("lavoro al forno", 1 / 15),                         # esempio: 15 kg di pane per ora di lavoro
            ("energia del forno (0,7 kWh)", 0.7 * kwh),
            ("sale, lievito e ammortamento del forno (5 centesimi)", 0.05 * h_euro)]
    print("\nEsempio: un chilo di pane")
    print("  grano: %.4f UCR per kg; farina: %.4f UCR per kg; 1 kWh acquistato: %.4f UCR" % (campo, farina, kwh))
    for nome, v in voci:
        print("  %-52s %.4f" % (nome, v))
    tot = sum(v for _, v in voci)
    print("  %-52s %.4f UCR = %.1f minuti" % ("totale", tot, tot * 60))


if __name__ == "__main__":
    stampa()
    esempio_pane()
