#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simulazione del Contributo di Riconoscenza (CdR).

Rifà i conti della bozza della tabella pubblica del CdR (bozze/tabella-cdr.md):

    python3 strumenti/simula_cdr.py

Regole simulate (Cod. 1, art. 44): un CdR conserva il valore pieno per dodici mesi, poi perde un quarto del
valore iniziale ogni trimestre e si estingue alla fine del ventiquattresimo mese; il saldo non supera il tetto.
"""

TETTO = 240                  # Cod. 1, art. 44, c. 2 (prima applicazione)
SETTIMANE_PER_MESE = 52 / 12
CONTRIBUTORI = 95            # Comunità di 150 persone (bozza dell'Allegato UCR)
ORE_PER_EURO = 0.0196        # coefficiente della bozza dell'Allegato UCR


def valore(mesi):
    """Quota del valore iniziale rimasta a un CdR maturato da `mesi` mesi compiuti.

    Il testo non dice quando avviene la prima riduzione. Qui cade alla fine del quindicesimo mese,
    l'unica lettura per cui il CdR si estingue «al termine del ventiquattresimo mese».
    """
    if mesi < 15:
        return 1.0
    if mesi < 18:
        return 0.75
    if mesi < 21:
        return 0.5
    if mesi < 24:
        return 0.25
    return 0.0


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
    fattore = sum(valore(m) for m in range(24))
    print("Curva: valore pieno per 15 mesi, poi 75%, 50%, 25%, zero al 24° mese")
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
    print("\nUn CdR vale una UCR: %.0f euro di acquisti esterni; il tetto: %.0f euro; %.1f settimane di CBO"
          % (1 / ORE_PER_EURO, TETTO / ORE_PER_EURO, TETTO / 15))
    print("Esempi di costo in UCR (prezzo per coefficiente; valori d'esempio)")
    for nome, euro in (("un chilo di caffè a 15 euro", 15), ("uno strumento musicale da 400 euro", 400),
                       ("un viaggio di 1.000 km in treno a 10 centesimi al km", 100)):
        print("  %-52s %.1f UCR" % (nome, euro * ORE_PER_EURO))


if __name__ == "__main__":
    stampa()
