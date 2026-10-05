# Progetto dei Cerchi

*[English version](README.en.md) · [Versión española](README.es.md)*

**Sito:** <https://imthezeroit.github.io/progetto-dei-cerchi/> — tutti i testi impaginati, in italiano e in inglese; il percorso anche in spagnolo. Per capire in un minuto di che cosa si tratta: [In un minuto](https://imthezeroit.github.io/progetto-dei-cerchi/#minuto).

Una proposta aperta di alternativa al modo in cui oggi organizziamo la vita collettiva.

Il progetto parte dalla persona, organizza la collettività e costruisce gli strumenti perché nessuna delle due debba dominare l'altra. È scritto per intero, articolo per articolo, perché possa essere letto, criticato, verificato e corretto.

**Stato:** fase di scrittura e verifica. I testi non sono un modello dimostrato: devono essere sperimentati, e dove falliscono vanno corretti.

## Da dove cominciare

Il percorso è fatto di quattro letture in sequenza.

1. [La storia umana](testi/it/percorso/1-la-storia-umana.md) — da dove veniamo.
2. [Analisi del presente](testi/it/percorso/2-analisi-del-presente.md) — dove siamo, in dati pubblici e verificabili.
3. [Il sistema contro l'individuo](testi/it/percorso/3-il-sistema-contro-l-individuo.md) — che cosa non funziona.
4. [Il Progetto dei Cerchi](testi/it/percorso/4-il-progetto-dei-cerchi.md) — che cosa proponiamo.

Poi vengono le regole.

## Il registro

| Testo | Versione |
|---|---|
| [Costituzione](testi/it/registro/costituzione.md) | V.29 |
| [Codice 1 — Contributo di base e Magazzini comuni](testi/it/registro/codice-01.md) | V1.5 |
| [Annex A al Codice 1 — Produzione materiale e officine](testi/it/registro/codice-01-annex-a.md) | V1.3 |
| [Codice 2 — Qualità e validazione](testi/it/registro/codice-02.md) | V1.5 |
| [Codice 3 — Deliberazione, soglie e Assemblea](testi/it/registro/codice-03.md) | V1.4 |
| [Codice 4 — Giustizia riparativa e garanzia](testi/it/registro/codice-04.md) | V1.4 |
| [Codice 5 — Apprendimento e competenze](testi/it/registro/codice-05.md) | V1.3 |
| [Codice 6 — Salute](testi/it/registro/codice-06.md) | V1.5 |
| [Codice 7 — Automazione e Rete](testi/it/registro/codice-07.md) | V1.6 |
| [Codice 8 — Energia e acqua](testi/it/registro/codice-08.md) | V1.3 |
| [Codice 9 — Agroecologia e alimentazione](testi/it/registro/codice-09.md) | V3.1 |
| [Codice 10 — Habitat e territorio](testi/it/registro/codice-10.md) | V1.3 |
| [Codice 11 — Logistica e mobilità di base](testi/it/registro/codice-11.md) | V1.3 |
| [Codice 12 — Cura di comunità](testi/it/registro/codice-12.md) | V1.3 |
| [Codice 13 — Biodiversità, santuari e fauna](testi/it/registro/codice-13.md) | V1.4 |
| [Codice 14 — Sicurezza generale](testi/it/registro/codice-14.md) | V1.2 |
| [Codice 15 — Rapporti esterni e Saldo](testi/it/registro/codice-15.md) | V1.3 |
| [Codice 16 — Transizione e avvio](testi/it/registro/codice-16.md) | V1.4 |
| [Allegato A al Codice 16 — Protocollo di avvio sociale](testi/it/registro/codice-16-allegato-a.md) | V1.3 |
| [Allegato B al Codice 16 — Manuale operativo di disinserimento e federazione](testi/it/registro/codice-16-allegato-b.md) | V1.5 |
| [Allegato C al Codice 16 — Carta operativa del primo anno](testi/it/registro/codice-16-allegato-c.md) | V1.0 |

La Costituzione stabilisce i principi e la struttura generale. I Codici trasformano quei principi in regole operative. Gli Allegati tecnici sviluppano procedure, criteri e specifiche. In caso di conflitto prevale la Costituzione.

Ogni modifica è annotata e motivata nel [registro delle modifiche](REGISTRO-DELLE-MODIFICHE.md). Lo storico di questo repository è l'archivio aperto, versionato e replicabile previsto dall'articolo 38.5 della Costituzione.

## Come è fatto questo repository

| Cartella | Contenuto |
|---|---|
| `testi/it/percorso/` | i quattro testi del percorso, in Markdown |
| `testi/it/registro/` | Costituzione, Codici e Allegati, in Markdown: sono la fonte di tutto il resto |
| `testi/en/` | la traduzione inglese degli stessi testi |
| `testi/es/` | la traduzione spagnola dei quattro testi del percorso |
| `docs/` | il sito, generato dai testi, in italiano (`docs/`), in inglese (`docs/en/`) e in spagnolo (`docs/es/`); contiene anche le versioni PDF e ODT da scaricare |
| `strumenti/` | il programma che genera il sito e il suo foglio di stile |

Per rigenerare il sito dopo una modifica ai testi servono Python 3 e [pandoc](https://pandoc.org):

```
python3 strumenti/costruisci.py
```

Il sito non usa servizi esterni, non carica caratteri o programmi dalla rete e non traccia chi lo visita.

## Lingue

Il testo che fa fede è quello italiano. Le versioni inglese e spagnola sono traduzioni di lavoro: i termini usati sono fissati in [`testi/en/GLOSSARY.md`](testi/en/GLOSSARY.md) e in [`testi/es/GLOSARIO.md`](testi/es/GLOSARIO.md). Quella spagnola comprende per ora i quattro testi del percorso; le regole sono in italiano e in inglese. Chi vuole rivederle o tradurre in altre lingue è benvenuto.

## Contribuire

Servono competenze diverse e, soprattutto, casi concreti con cui mettere alla prova le regole. Vedi [CONTRIBUIRE.md](CONTRIBUIRE.md) e le [segnalazioni aperte](https://github.com/ImTheZeroIt/progetto-dei-cerchi/issues). Chi non ha un account su GitHub può scrivere a [zerocirclesproject@gmail.com](mailto:zerocirclesproject@gmail.com).

## Licenza

- **Costituzione, Codici e Allegati:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.it). Si possono copiare, modificare e ripubblicare, citando la fonte e mantenendo la stessa licenza.
- **I quattro testi del percorso:** [CC BY-ND 4.0](https://creativecommons.org/licenses/by-nd/4.0/deed.it). Si possono copiare e ripubblicare per intero, citando la fonte, ma non modificare. Si possono tradurre in altre lingue, se la traduzione è integrale e fedele.

Vedi [LICENSE.md](LICENSE.md).
