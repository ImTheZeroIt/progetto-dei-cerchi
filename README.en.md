# The Circles Project

*[Versione italiana](README.md) · [Versión española](README.es.md)*

**Website:** <https://imthezeroit.github.io/progetto-dei-cerchi/en/> — all the texts, laid out for reading, in Italian and in English; the path also in Spanish. To see in one minute what this is about: [In one minute](https://imthezeroit.github.io/progetto-dei-cerchi/en/#minuto).

An open proposal for an alternative to the way we organise collective life today.

The project starts from the person, organises the collectivity and builds the tools so that neither has to dominate the other. It is written out in full, article by article, so that it can be read, criticised, verified and corrected.

**Status:** writing and verification. The texts are not a proven model: they must be tested, and corrected where they fail.

**Translation:** this English version is a working translation. The Italian text is the authoritative one. The terminology is fixed in [`testi/en/GLOSSARY.md`](testi/en/GLOSSARY.md).

## Where to start

The path is made of four readings in sequence.

1. [Human history](testi/en/path/1-human-history.md) — where we come from.
2. [Analysis of the present](testi/en/path/2-analysis-of-the-present.md) — where we are, in public and verifiable data.
3. [The system against the individual](testi/en/path/3-the-system-against-the-individual.md) — what does not work.
4. [The Circles Project](testi/en/path/4-the-circles-project.md) — what we propose.

Then come the rules.

## The register

| Text | Version |
|---|---|
| [Constitution](testi/en/register/constitution.md) | V.29 |
| [Code 1 — Base contribution and Common Storehouses](testi/en/register/code-01.md) | V1.5 |
| [Annex A to Code 1 — Material production and workshops](testi/en/register/code-01-annex-a.md) | V1.3 |
| [Code 2 — Quality and validation](testi/en/register/code-02.md) | V1.5 |
| [Code 3 — Deliberation, thresholds and Assembly](testi/en/register/code-03.md) | V1.4 |
| [Code 4 — Restorative justice and guarantee](testi/en/register/code-04.md) | V1.4 |
| [Code 5 — Learning and competences](testi/en/register/code-05.md) | V1.3 |
| [Code 6 — Health](testi/en/register/code-06.md) | V1.5 |
| [Code 7 — Automation and the Network](testi/en/register/code-07.md) | V1.6 |
| [Code 8 — Energy and water](testi/en/register/code-08.md) | V1.3 |
| [Code 9 — Agroecology and food](testi/en/register/code-09.md) | V3.1 |
| [Code 10 — Habitat and territory](testi/en/register/code-10.md) | V1.3 |
| [Code 11 — Logistics and basic mobility](testi/en/register/code-11.md) | V1.3 |
| [Code 12 — Community care](testi/en/register/code-12.md) | V1.3 |
| [Code 13 — Biodiversity, sanctuaries and fauna](testi/en/register/code-13.md) | V1.4 |
| [Code 14 — General safety](testi/en/register/code-14.md) | V1.2 |
| [Code 15 — External relations and Balance](testi/en/register/code-15.md) | V1.3 |
| [Code 16 — Transition and launch](testi/en/register/code-16.md) | V1.4 |
| [Annex A to Code 16 — Social start-up protocol](testi/en/register/code-16-annex-a.md) | V1.3 |
| [Annex B to Code 16 — Operating manual for disengagement and federation](testi/en/register/code-16-annex-b.md) | V1.5 |
| [Annex C to Code 16 — First-year operating charter](testi/en/register/code-16-annex-c.md) | V1.0 |

The Constitution sets out the principles and the general structure. The Codes turn those principles into operating rules. The Technical Annexes develop procedures, criteria and specifications. In case of conflict, the Constitution prevails.

Every change is recorded and explained in the [change log](CHANGELOG.md). The proposed numbers, with their origin and the test each would need, are in the [register of parameters to be verified](PARAMETRI.md) (for now in Italian).

## How this repository is organised

| Folder | Contents |
|---|---|
| `testi/it/` | the Italian texts (authoritative), in Markdown |
| `testi/en/` | the English translation and its glossary |
| `testi/es/` | the Spanish translation of the four texts of the path, and its glossary |
| `docs/` | the website, generated from the texts: Italian in `docs/`, English in `docs/en/`, Spanish in `docs/es/`, with PDF and ODT downloads |
| `strumenti/` | the program that generates the website, and its style sheet |

To rebuild the website after changing a text you need Python 3 and [pandoc](https://pandoc.org):

```
python3 strumenti/costruisci.py
```

The website uses no external services, loads no fonts or scripts from the network and does not track visitors.

## Contributing

Different skills are needed and, above all, concrete cases with which to put the rules to the test. See [CONTRIBUTING.md](CONTRIBUTING.md) and the [open issues](https://github.com/ImTheZeroIt/progetto-dei-cerchi/issues). Those without a GitHub account can write to [zerocirclesproject@gmail.com](mailto:zerocirclesproject@gmail.com).

## Licence

- **Constitution, Codes and Annexes:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). They may be copied, modified and republished, citing the source and keeping the same licence.
- **The four texts of the path:** [CC BY-ND 4.0](https://creativecommons.org/licenses/by-nd/4.0/). They may be copied and republished in full, citing the source, but not modified. They may be translated into other languages, provided the translation is complete and faithful.

See [LICENSE.md](LICENSE.md).
