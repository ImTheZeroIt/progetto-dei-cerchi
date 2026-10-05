#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simulazione del Contributo di Riconoscenza (CdR).

Rifà i conti della bozza della tabella pubblica del CdR (bozze/tabella-cdr.md):

    python3 strumenti/simula_cdr.py

Regole simulate (Cod. 1, art. 44): un CdR conserva il valore pieno per dodici mesi, poi perde un quarto del
valore iniziale ogni trimestre e si estingue alla fine del ventiquattresimo mese; il saldo non supera il tetto.

Il testo ammette tre letture del modo in cui il valore scende (vedi LETTURE). La simulazione usa quella
graduale: dal compimento del dodicesimo mese il valore scende in proporzione al tempo, un dodicesimo al mese,
fino a zero al compimento del ventiquattresimo. È la sola che rispetta sia i dodici mesi pieni sia
l'estinzione al ventiquattresimo, ed è la lettura della proposta di modifica 9. Per provare le altre basta
cambiare LETTURA.
"""

LETTURA = "graduale"         # "graduale", "fine trimestre" oppure "inizio trimestre"

TETTO = 240                  # Cod. 1, art. 44, c. 2 (prima applicazione)
SETTIMANE_PER_MESE = 52 / 12
CONTRIBUTORI = 95            # Comunità di 150 persone (bozza dell'Allegato UCR)
ORE_PER_EURO = 0.0196        # coefficiente dell'Unione europea (bozza dell'Allegato UCR)

# Prodotto per abitante nel 2024, in dollari correnti (Banca Mondiale, NY.GDP.PCAP.CD).
# Il coefficiente di un paese è quello europeo moltiplicato per il rapporto tra il prodotto per abitante
# dell'UE e quello del paese. Ipotesi: le ore lavorate per abitante sono le stesse dell'UE.
PRODOTTO_PER_ABITANTE = {"Unione europea": 43313.77, "Brasile": 10310.55, "Cina": 13293.12, "Vietnam": 4716.66,
                         "Indonesia": 4925.44, "Costa d'Avorio": 2727.89, "India": 2591.99,
                         "Bangladesh": 2593.42, "Etiopia": 1133.88, "Ruanda": 1059.94}


def coefficiente(paese):
    """Ore di lavoro per euro di prodotto in un paese."""
    return ORE_PER_EURO * PRODOTTO_PER_ABITANTE["Unione europea"] / PRODOTTO_PER_ABITANTE[paese]


def ore_caffe():
    """Ore di piantagione in un chilo di caffè tostato.

    Ruanda (Organizzazione internazionale del caffè): 251,4 giornate per ettaro, 1,69 kg di ciliegie per pianta.
    Ipotesi: 2.500 piante per ettaro, giornate di 7 ore, 6 kg di ciliegie per kg di caffè verde,
    1,19 kg di verde per kg di tostato.
    """
    return 251.4 * 7 / 4225 * 6 * 1.19


def valore(mesi, lettura=None):
    """Quota del valore iniziale di un CdR maturato da `mesi` mesi compiuti, in media durante il mese seguente.

    graduale:         pieno per dodici mesi, poi scende in proporzione al tempo; zero al compimento del 24°.
    fine trimestre:   pieno per quindici mesi, poi 75%, 50%, 25%; zero al 24°.
    inizio trimestre: pieno per dodici mesi, poi 75%, 50%, 25%; zero al 21°.
    """
    lettura = lettura or LETTURA
    if lettura == "graduale":
        return 1.0 if mesi < 12 else max(0.0, (23.5 - mesi) / 12)
    passo = 15 if lettura == "fine trimestre" else 12
    if mesi < passo:
        return 1.0
    return max(0.0, 0.75 - 0.25 * ((mesi - passo) // 3))


def valore_al_compimento(mesi):
    """Lettura graduale: valore esatto al compimento di `mesi` mesi."""
    return 1.0 if mesi <= 12 else max(0.0, (24 - mesi) / 12)


LETTURE = ("graduale", "fine trimestre", "inizio trimestre")


def saldo(cdr_al_mese, mesi, tetto=TETTO):
    """Saldo dopo `mesi` mesi per chi matura ogni mese la stessa quantità e non impiega mai nulla."""
    lotti = []                                   # [età in mesi, valore iniziale]
    for _ in range(mesi):
        for lotto in lotti:
            lotto[0] += 1
        lotti = [l for l in lotti if valore(l[0]) > 0]
        attuale = sum(v * valore(e) for e, v in lotti)
        nuovo = cdr_al_mese if tetto is None else max(0.0, min(cdr_al_mese, tetto - attuale))
        lotti.append([0, nuovo])
    return sum(v * valore(e) for e, v in lotti)


def mesi_al_tetto(cdr_al_mese):
    for m in range(1, 241):
        if saldo(cdr_al_mese, m) >= TETTO - 1e-9:
            return m
    return None


def stampa():
    print("Le tre letture dell'art. 44, c. 3: mesi di maturazione conservati a regime e ore a settimana per il tetto")
    for lettura in LETTURE:
        f = sum(valore(m, lettura) for m in range(24))
        print("  %-17s %4.1f mesi; tetto con %.1f ore a settimana%s"
              % (lettura, f, TETTO / f / SETTIMANE_PER_MESE, "   <- usata qui" if lettura == LETTURA else ""))
    fattore = sum(valore(m) for m in range(24))
    print("\nLettura graduale, valore al compimento dei mesi: %s"
          % ", ".join("%d: %.0f%%" % (m, 100 * valore_al_compimento(m)) for m in (12, 15, 18, 21, 24)))
    print("A regime, chi non impiega mai i CdR ne conserva %.1f mesi di maturazione" % fattore)
    soglia = TETTO / fattore
    print("Il tetto di %d si raggiunge maturando %.1f CdR al mese: %.1f ore a settimana oltre il CBO"
          % (TETTO, soglia, soglia / SETTIMANE_PER_MESE))
    print("\nSaldo di chi lavora ogni settimana le stesse ore oltre il CBO e non impiega mai i CdR")
    print("  %-22s %8s %8s %10s %s" % ("ore a settimana", "1 anno", "2 anni", "a regime", "mesi per il tetto"))
    for ore in (0.5, 1, 2, 3, 5, 8):
        al_mese = ore * SETTIMANE_PER_MESE
        m = mesi_al_tetto(al_mese)
        print("  %-22s %8.0f %8.0f %10.0f %s" % (ore, saldo(al_mese, 12), saldo(al_mese, 24), saldo(al_mese, 60),
                                                  m if m else "mai"))
    print("\nMaggiorazioni dentro il CBO (15 ore a settimana), senza altro lavoro")
    for quota, magg in ((0.2, 0.3), (0.2, 0.5), (0.2, 1.0), (1.0, 0.5), (1.0, 1.0)):
        al_mese = 15 * quota * magg * SETTIMANE_PER_MESE
        m = mesi_al_tetto(al_mese)
        print("  %3.0f%% delle ore in compiti maggiorati del %3.0f%%: %5.1f CdR al mese; a regime %3.0f; tetto: %s"
              % (100 * quota, 100 * magg, al_mese, saldo(al_mese, 60), ("dopo %d mesi" % m) if m else "mai"))
    print("\nDistribuzione in una Comunità di %d contributori, dopo cinque anni" % CONTRIBUTORI)
    profili = [(0.50, 0), (0.30, 1), (0.15, 3), (0.05, 8)]      # quota di persone, ore a settimana oltre il CBO
    for nome, tetto in (("con il tetto", TETTO), ("senza tetto", None)):
        saldi = [(q * CONTRIBUTORI, saldo(o * SETTIMANE_PER_MESE, 60, tetto)) for q, o in profili]
        totale = sum(n * s for n, s in saldi)
        primi = saldi[-1][0] * saldi[-1][1]
        print("  %s: totale %5.0f CdR; il 5%% più attivo ne detiene il %2.0f%%"
              % (nome, totale, 100 * primi / totale))
        for (q, o), (n, s) in zip(profili, saldi):
            print("     %2.0f%% delle persone, %d ore a settimana: saldo %3.0f" % (100 * q, o, s))
    print("\nSe il tetto fosse diverso (stessa Comunità, nessuno impiega i CdR)")
    for tetto in (120, 180, 240, 300, 360, 480):
        saldi = [(q * CONTRIBUTORI, saldo(o * SETTIMANE_PER_MESE, 60, tetto)) for q, o in profili]
        totale = sum(n * s for n, s in saldi)
        quota = saldi[-1][0] * saldi[-1][1] / totale
        al_tetto = sum(n for n, s in saldi if s >= tetto - 1e-6) / CONTRIBUTORI
        print("  tetto %3d: si raggiunge con %.1f ore a settimana; persone al tetto %2.0f%%; quota del 5%% più attivo %2.0f%%%s"
              % (tetto, tetto / fattore / SETTIMANE_PER_MESE, 100 * al_tetto, 100 * quota,
                 "  <- oltre la soglia di un quinto" if quota > 0.2 else ""))
    print("\nUn CdR vale una UCR: %.0f euro di acquisti esterni; il tetto: %.0f euro; %.1f settimane di CBO"
          % (1 / ORE_PER_EURO, TETTO / ORE_PER_EURO, TETTO / 15))
    print("\nOre di lavoro per euro, per paese di produzione")
    for paese in PRODOTTO_PER_ABITANTE:
        print("  %-16s %.3f  (un'ora ogni %.1f euro)" % (paese, coefficiente(paese), 1 / coefficiente(paese)))
    print("\nCosto in UCR di beni e servizi non necessari (valori d'esempio)")
    m2_anno = 750 / 80 * ORE_PER_EURO + 4427 / (150 * 20)    # materiali più manutenzione, per m2 all'anno
    ue, cina = ORE_PER_EURO, coefficiente("Cina")
    righe = [
        ("un chilo di caffè (15 euro): ore di piantagione più 13 euro in Europa", ore_caffe() + 13 * ue, 15 * ue),
        ("un chilo di cioccolato (12 euro): un quinto del prezzo in Costa d'Avorio",
         12 * 0.2 * coefficiente("Costa d'Avorio") + 12 * 0.8 * ue, 12 * ue),
        ("un libro stampato in Europa (18 euro)", 18 * ue, 18 * ue),
        ("materiali europei per un'opera o un progetto personale (100 euro)", 100 * ue, 100 * ue),
        ("uno strumento musicale fatto in Europa (400 euro)", 400 * ue, 400 * ue),
        ("lo stesso strumento, metà del prezzo in Cina", 200 * cina + 200 * ue, 400 * ue),
        ("un apparecchio oltre la dotazione di base (500 euro in più), metà in Cina", 250 * cina + 250 * ue, 500 * ue),
        ("una macchina fotografica (600 euro), metà in Cina", 300 * cina + 300 * ue, 600 * ue),
        ("una bicicletta da viaggio fatta in Europa (1.200 euro)", 1200 * ue, 1200 * ue),
        ("la stessa bicicletta, metà del prezzo in Cina", 600 * cina + 600 * ue, 1200 * ue),
        ("un viaggio di 1.000 km in treno (10 centesimi al km)", 100 * ue, 100 * ue),
        ("un viaggio di 5.000 km in treno", 500 * ue, 500 * ue),
        ("una notte di ospitalità ordinaria in Casa Ponte (15 m2 e mezz'ora di gestione)", 15 * m2_anno / 365 + 0.5, None),
        ("quattordici notti in Casa Ponte", 14 * (15 * m2_anno / 365 + 0.5), None),
        ("uso esclusivo di uno spazio comune di 20 m2 per tre mesi", 20 * m2_anno / 4, None),
        ("uso esclusivo di uno spazio comune di 20 m2 per un anno", 20 * m2_anno, None),
    ]
    print("  uno spazio comune costa %.2f UCR per m2 all'anno; un chilo di caffè contiene %.1f ore di piantagione"
          % (m2_anno, ore_caffe()))
    print("  %-78s %6s %s" % ("", "UCR", "(con la sola media europea)"))
    for nome, ucr, media in righe:
        print("  %-78s %6.1f %s" % (nome, ucr, ("(%.1f)" % media) if media is not None and abs(media - ucr) > 0.05 else ""))
    piu_caro = max(u for _, u, _ in righe)
    print("  la voce più costosa vale %.0f UCR: il tetto è %.1f volte tanto" % (piu_caro, TETTO / piu_caro))
    print("  un bene fatto per metà in Cina contiene %.1f volte le ore indicate dalla media europea"
          % ((0.5 * cina + 0.5 * ue) / ue))


if __name__ == "__main__":
    stampa()
