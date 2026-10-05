/* Ricerca nei testi del Progetto dei Cerchi.
   Gira tutta nel browser: nessuna domanda viene inviata o registrata, nessun servizio esterno.
   Non è un'intelligenza artificiale. Confronta le parole della domanda con i testi, divisi per articolo,
   e mette in ordine i passi con un punteggio noto (BM25). I dati stanno in assets/indice-<lingua>.js,
   scritto da strumenti/costruisci.py. */
(function () {
  "use strict";
  var dati = window.CERCHI_INDICE;
  var modulo = document.getElementById("cerca-form");
  var campo = document.getElementById("q");
  var esito = document.getElementById("cerca-esito");
  var frequenti = document.getElementById("frequenti");
  if (!dati || !modulo || !campo || !esito) return;
  var L = dati.lingua, T = dati.t;

  /* ---------- parole da ignorare e sinonimi, per lingua */
  var VUOTE = {
    it: "a ad al allo alla ai agli alle anche c che chi ci come con cosa cos cui da dal dallo dalla dai dagli dalle de dei del dello della degli delle di dove e ed è era essere fa gli ha hanno ho i il in io l la le lei li lo loro lui ma mi mia mie miei mio ne nei nel nello nella negli nelle no noi non o per perché piu più posso puo può qual quale quali quando quanto quanta quante quanti quello quella questo questa se sei si sia sono su sua sue sul sullo sulla sui sugli sulle suo suoi ti tra tu tua tuo tuoi un una uno vi voi d succede esiste esistono devo deve qualcosa",
    en: "a an and are as at be but by can do does for from has have how i if in is it its me my no not of on or our so than that the their them then there these they this to up was we what when where which who why will with you your about any should would could am did",
    es: "a al algo como con cual cuál cuando cuánto de del donde dónde e el ella ellos en es esta este esto hay la las lo los me mi mis no nos o para pero por porque qué que quien quién se si sí sin sobre son su sus te tu tus un una uno y ya puedo puede debo hace"
  };
  var SINONIMI = {
    it: {
      soldi: "denaro cassa pagamento", moneta: "denaro", euro: "denaro", stipendio: "compenso reddito cdr", salario: "compenso reddito",
      paga: "compenso", lavoro: "cbo contributo", lavorare: "cbo contributo", casa: "alloggio abitazione", affitto: "alloggio rendita",
      prigione: "contenimento", carcere: "contenimento", galera: "contenimento", polizia: "tutela civica corpo", tasse: "fiscali imposte",
      fisco: "fiscali", scuola: "apprendimento alfabetizzazione", medico: "salute cure sanitari", dottore: "salute cure", ospedale: "salute cure",
      chiesa: "religione culto", dio: "religione credo", fede: "religione credo", vegano: "vegetale animali", carne: "macellazione animali",
      capo: "coordinamento portavoce", governo: "assemblea coordinamento", presidente: "portavoce coordinamento", eredita: "ereditabile morte successione",
      robot: "automazione macchine", figli: "minori", bambini: "minori", anziani: "eta esenzione", pensione: "esenzione eta redditi",
      uscire: "lasciare appartenere riammessa", andarsene: "lasciare appartenere riammessa", andarmene: "lasciare appartenere riammessa",
      andare: "lasciare", tornare: "riammessa riammissione", rientrare: "riammessa riammissione", uscita: "lasciare appartenere", voto: "deliberazione assemblea", privacy: "dati sorveglianza",
      internet: "rete connettivita", telefono: "connettivita rete", cibo: "alimenti paniere", mangiare: "alimenti paniere", luce: "energia",
      corrente: "energia", terra: "suolo", terreno: "suolo", guerra: "difesa disarmo armi", ricchi: "accumulo", ricchezza: "accumulo",
      impresa: "proprieta uso", azienda: "proprieta uso", negozio: "magazzini", droga: "salute", matrimonio: "cerchio nucleo", famiglia: "nucleo cerchio",
      vecchi: "eta esenzione", malati: "salute sospensione", disabili: "disabilita fragilita", stranieri: "non confederata ospitalita",
      immigrati: "non confederata ospitalita", ia: "intelligenza artificiale", ai: "ia intelligenza artificiale", sesso: "consenso", auto: "mobilita veicoli"
    },
    en: {
      money: "cash payment fund", salary: "income cdr", wage: "income cdr", wages: "income cdr", job: "cbo contribution work", work: "cbo contribution",
      house: "dwelling housing home", rent: "dwelling rent", prison: "containment", jail: "containment", police: "civic protection corps",
      tax: "fiscal", taxes: "fiscal", school: "learning literacy", doctor: "health care", hospital: "health care", church: "religion worship",
      god: "religion belief", vegan: "plant animals", meat: "slaughter animals", boss: "coordination spokesperson", government: "assembly coordination",
      president: "spokesperson", inheritance: "inheritable death", robot: "automation machines", robots: "automation machines", kids: "minors children",
      children: "minors", elderly: "age exemption", pension: "exemption income", leave: "withdraw belong", vote: "deliberation assembly",
      privacy: "data surveillance", internet: "network connectivity", phone: "connectivity network", food: "foodstuffs basket", war: "defence disarmament weapons",
      guns: "weapons", business: "ownership use", company: "ownership use", shop: "storehouse", family: "nucleus circle", ai: "artificial intelligence"
    },
    es: {
      dinero: "moneda", trabajo: "contribución", casa: "vivienda", cárcel: "contención", policía: "tutela", impuestos: "fiscales",
      escuela: "aprendizaje", médico: "salud", iglesia: "religión", carne: "animales", jefe: "coordinación", gobierno: "asamblea"
    }
  };

  /* modi di dire che non portano informazione */
  var MODI = { it: ["per forza", "in che modo", "che fine fa", "che fine fanno"], en: ["have to", "what about"], es: ["a la fuerza"] };

  /* ---------- parole e radici */
  function semplice(s) {
    return s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
  }
  function parole(s) {
    return semplice(s).replace(/['’`]/g, " ").split(/[^a-z0-9]+/).filter(function (p) { return p.length > 1; });
  }
  var SUFFISSI = {
    it: ["azione", "azioni", "amento", "amenti", "mente", "abile", "abili", "ibile", "ibili", "are", "ere", "ire", "ato", "ata", "ati", "ate",
         "uto", "uta", "uti", "ute", "ito", "ita", "iti", "ite", "ano", "ono", "ando", "endo"],
    en: ["ations", "ation", "ments", "ment", "ings", "ing", "ies", "ed", "es", "s"],
    es: ["aciones", "ación", "acion", "mente", "ados", "adas", "idos", "idas", "ado", "ada", "ido", "ida", "ar", "er", "ir", "es", "s"]
  };
  function radice(p) {
    var s = SUFFISSI[L] || [], i;
    if (/^\d/.test(p)) return p;
    var lunga = L === "en" ? 3 : 5, resto = L === "en" ? 3 : 4;
    if (p.length > lunga) {
      for (i = 0; i < s.length; i++) {
        if (p.length - s[i].length >= resto && p.slice(-s[i].length) === s[i]) { p = p.slice(0, -s[i].length); break; }
      }
    }
    if (L === "en") { if (p.length > 4 && /e$/.test(p)) p = p.slice(0, -1); }
    else if (p.length > 3 && /[aeio]$/.test(p)) p = p.slice(0, -1);
    return p;
  }
  var vuote = {};
  parole(VUOTE[L] || "").forEach(function (p) { vuote[p] = 1; });
  function radici(testo) {
    return parole(testo).filter(function (p) { return !vuote[p]; }).map(radice);
  }
  var sinonimi = {};
  Object.keys(SINONIMI[L] || {}).forEach(function (k) {
    sinonimi[radice(semplice(k))] = radici(SINONIMI[L][k]);
  });

  /* ---------- indice */
  function Indice(elementi, testoDi) {
    this.n = elementi.length; this.voci = {}; this.lunghezze = []; var totale = 0, me = this;
    elementi.forEach(function (el, i) {
      var conteggi = {}, lunghezza = 0;
      testoDi(el).forEach(function (coppia) {
        radici(coppia[0]).forEach(function (r) { conteggi[r] = (conteggi[r] || 0) + coppia[1]; lunghezza += coppia[1]; });
      });
      me.lunghezze.push(lunghezza); totale += lunghezza;
      Object.keys(conteggi).forEach(function (r) { (me.voci[r] = me.voci[r] || []).push([i, conteggi[r]]); });
    });
    this.media = totale / Math.max(1, this.n);
    this.chiavi = Object.keys(this.voci).sort();
  }
  Indice.prototype.cerca = function (termini) {
    var punti = {}, coperti = {}, me = this, k1 = 1.2, b = 0.6;
    termini.forEach(function (t, numero) {
      var elenco = me.voci[t.r];
      if (!elenco && t.r.length >= 5) {                    // nessuna parola uguale: provo con l'inizio della parola
        elenco = [];
        var inizio = t.r.slice(0, Math.max(5, t.r.length - 2));
        me.chiavi.forEach(function (c) { if (c.indexOf(inizio) === 0) elenco = elenco.concat(me.voci[c]); });
        if (!elenco.length) elenco = null;
      }
      if (!elenco) return;
      var idf = Math.log(1 + (me.n - elenco.length + 0.5) / (elenco.length + 0.5));
      elenco.forEach(function (v) {
        var tf = v[1], norma = k1 * (1 - b + b * me.lunghezze[v[0]] / me.media);
        punti[v[0]] = (punti[v[0]] || 0) + t.peso * idf * tf * (k1 + 1) / (tf + norma);
        if (t.gruppo !== undefined) { (coperti[v[0]] = coperti[v[0]] || {})[t.gruppo] = 1; }
      });
    });
    var gruppi = {}; termini.forEach(function (t) { gruppi[t.gruppo] = 1; });
    var quanti = Object.keys(gruppi).length || 1;
    return Object.keys(punti).map(function (i) {
      var copertura = Object.keys(coperti[i] || {}).length / quanti;
      return { i: +i, punti: punti[i] * (0.35 + 0.65 * copertura) * me.peso(+i), copertura: copertura };
    }).sort(function (a, b) { return b.punti - a.punti; });
  };

  var indiceTesti = null, indiceDomande = null;
  function prepara() {
    if (indiceTesti) return;
    indiceTesti = new Indice(dati.unita, function (u) { return [[u[2], 3], [u[4], 1]]; });
    indiceTesti.peso = function (i) { return dati.docs[dati.unita[i][0]][2] || 1; };   // prima le regole, poi le bozze
    indiceDomande = new Indice(dati.domande, function (d) { return [[d.q, 4], [d.k.join(" "), 4], [d.x, 1]]; });
    indiceDomande.peso = function () { return 1; };
  }

  function termini(domanda) {
    var visti = {}, uscita = [], gruppo = 0;
    (MODI[L] || []).forEach(function (modo) { domanda = semplice(domanda).split(modo).join(" "); });
    var elenco = radici(domanda);
    if (!elenco.length) elenco = parole(domanda).map(radice);     // solo parole comuni: le uso lo stesso
    elenco.forEach(function (r) {
      if (visti[r]) return;
      visti[r] = 1; uscita.push({ r: r, peso: 1, gruppo: gruppo });
      (sinonimi[r] || []).forEach(function (s) {
        if (!visti[s]) { visti[s] = 1; uscita.push({ r: s, peso: 0.45, gruppo: gruppo }); }
      });
      gruppo++;
    });
    return uscita;
  }

  /* ---------- presentazione */
  function sicuro(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
  function evidenzia(testo, insieme) {
    return testo.split(/([A-Za-zÀ-ÿ0-9]+)/).map(function (pezzo, i) {
      if (i % 2 === 0) return sicuro(pezzo);
      var p = semplice(pezzo);
      return (!vuote[p] && insieme[radice(p)]) ? "<mark>" + sicuro(pezzo) + "</mark>" : sicuro(pezzo);
    }).join("");
  }
  function passo(testo, insieme) {
    var righe = testo.split("\n"), migliore = 0, massimo = -1;
    righe.forEach(function (riga, i) {
      var trovate = {}, n = 0;
      radici(riga).forEach(function (r) { if (insieme[r] && !trovate[r]) { trovate[r] = 1; n++; } });
      if (n > massimo) { massimo = n; migliore = i; }
    });
    var riga = righe[migliore];
    if (riga.length < 110 && righe[migliore + 1]) riga += " " + righe[migliore + 1];
    if (riga.length > 330) {
      var pos = 0, parti = riga.split(/([A-Za-zÀ-ÿ0-9]+)/), conto = 0;
      for (var i = 1; i < parti.length; i += 2) {
        if (insieme[radice(semplice(parti[i]))]) { pos = conto; break; }
        conto += parti[i].length + (parti[i + 1] || "").length;
      }
      var da = Math.max(0, pos - 110);
      if (da > 0) da = riga.indexOf(" ", da) + 1;
      riga = (da > 0 ? "… " : "") + riga.slice(da, da + 320) + (da + 320 < riga.length ? " …" : "");
    }
    return evidenzia(riga, insieme);
  }

  var ultimi = [], mostrati = 0;
  function mostraTesti(insieme) {
    var html = "", fino = Math.min(ultimi.length, mostrati);
    for (var n = 0; n < fino; n++) {
      var u = dati.unita[ultimi[n].i], doc = dati.docs[u[0]];
      var titolo = sicuro(doc[0]) + (u[2] ? " · " + sicuro(u[2]) : "") + (u[3] ? " · " + T.comma + " " + sicuro(u[3]) : "");
      html += '<li><a class="dove-titolo" href="' + sicuro(doc[1] + (u[1] ? "#" + u[1] : "")) + '">' + titolo + "</a>" +
              "<p>" + passo(u[4], insieme) + "</p></li>";
    }
    return html;
  }

  function cerca(domanda, aggiornaIndirizzo) {
    domanda = domanda.trim();
    if (!domanda) { esito.innerHTML = ""; if (frequenti) frequenti.hidden = false; return; }
    prepara();
    var ter = termini(domanda), insieme = {};
    ter.forEach(function (t) { insieme[t.r] = 1; });
    var html = "";
    var risposte = [];
    if (radici(domanda).length) risposte = indiceDomande.cerca(ter).filter(function (r) { return r.copertura >= 0.5; });
    var scritta = parole(domanda).join(" ");               // la domanda è proprio una di quelle dell'elenco?
    if (scritta.length >= 6) {
      var uguali = [];
      dati.domande.forEach(function (d, i) {
        if ((" " + parole(d.q).join(" ") + " ").indexOf(" " + scritta + " ") >= 0) uguali.push({ i: i, punti: 1e9 - i, copertura: 1 });
      });
      if (uguali.length) risposte = uguali.concat(risposte.filter(function (r) { return !uguali.some(function (u) { return u.i === r.i; }); }));
    }
    var citati = [];                                        // gli articoli richiamati dalle risposte brevi
    if (risposte.length) {
      var soglia = risposte[0].punti * 0.6;
      html += "<h2>" + T.h_risposta + "</h2>";
      risposte.filter(function (r) { return r.punti >= soglia; }).slice(0, 2).forEach(function (r) {
        var d = dati.domande[r.i];
        html += '<article class="risposta-breve"><h3>' + sicuro(d.q) + "</h3>" + d.h + "</article>";
        (d.r || []).forEach(function (u) { if (citati.indexOf(u) < 0) citati.push(u); });
      });
    }
    ultimi = indiceTesti.cerca(ter).filter(function (r) { return r.copertura > 0; });
    if (citati.length) {                                    // vengono per primi, nell'ordine della risposta
      var cima = (ultimi[0] ? ultimi[0].punti : 1) * 2, presenti = {};
      ultimi.forEach(function (r) {
        var u = dati.unita[r.i], n = citati.indexOf(dati.docs[u[0]][1] + "#" + u[1]);
        if (n >= 0 && !presenti[n]) { presenti[n] = 1; r.punti = cima - n * 1e-3; r.copertura = 1; }
      });
      dati.unita.forEach(function (u, i) {
        var n = citati.indexOf(dati.docs[u[0]][1] + "#" + u[1]);
        if (n >= 0 && !presenti[n]) { presenti[n] = 1; ultimi.push({ i: i, punti: cima - n * 1e-3, copertura: 1 }); }
      });
      ultimi.sort(function (a, b) { return b.punti - a.punti; });
    }
    if (ultimi.length) {
      var migliore = ultimi[0].copertura, gia = {};
      ultimi = ultimi.filter(function (r) {                 // un solo risultato per articolo o per pagina
        var u = dati.unita[r.i], chiave = u[0] + "#" + u[1];
        if (r.copertura < Math.min(migliore, 0.5) || gia[chiave]) return false;
        gia[chiave] = 1; return true;
      }).slice(0, 40);
    }
    mostrati = 6;
    if (ultimi.length) {
      html += "<h2>" + T.h_testi + "</h2>" +
              '<p class="cerca-conto">' + (ultimi.length === 1 ? T.un_risultato : T.risultati.replace("{n}", ultimi.length >= 40 ? "40+" : ultimi.length)) + "</p>" +
              '<ol class="cerca-risultati" id="cerca-risultati">' + mostraTesti(insieme) + "</ol>" +
              (ultimi.length > mostrati ? '<p><button type="button" class="secondario-bottone" id="cerca-altri">' + T.altri + "</button></p>" : "");
    }
    if (!html) html = '<p class="cerca-vuoto">' + T.nessuno + " " + T.nessuno_aiuto + "</p>";
    html += '<p class="cerca-tutte"><a href="#frequenti" id="cerca-tutte">' + T.tutte + "</a></p>";
    esito.innerHTML = html;
    if (frequenti) frequenti.hidden = true;
    var altri = document.getElementById("cerca-altri");
    if (altri) altri.addEventListener("click", function () {
      mostrati += 8;
      document.getElementById("cerca-risultati").innerHTML = mostraTesti(insieme);
      if (mostrati >= ultimi.length) altri.parentNode.removeChild(altri);
    });
    var tutte = document.getElementById("cerca-tutte");
    if (tutte) tutte.addEventListener("click", function () { if (frequenti) frequenti.hidden = false; });
    if (aggiornaIndirizzo && window.history && history.replaceState) {
      history.replaceState(null, "", location.pathname + "?q=" + encodeURIComponent(domanda));
    }
  }

  modulo.addEventListener("submit", function (evento) {
    evento.preventDefault();
    cerca(campo.value, true);
  });
  campo.addEventListener("search", function () { if (!campo.value) cerca("", false); });

  var iniziale = /[?&]q=([^&]*)/.exec(location.search);
  if (iniziale) {
    campo.value = decodeURIComponent(iniziale[1].replace(/\+/g, " "));
    cerca(campo.value, false);
  } else if (location.hash && location.hash.indexOf("#d-") === 0) {
    var aperta = document.getElementById(location.hash.slice(1));
    if (aperta) aperta.open = true;
  }
})();
