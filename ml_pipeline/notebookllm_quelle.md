# JumpOne – KI-basierte Win-Prediction: Projektdokumentation

## Projektübersicht

**Projekttitel:** Echtzeit-Gewinnwahrscheinlichkeits-Vorhersage für das Jump-and-Run-Spiel „JumpOne"  
**Technologie-Stack:** TypeScript/Phaser (Spiel), Python/XGBoost (ML), Supabase (Telemetrie-Datenbank)  
**Ziel:** Ein ML-Modell, das während einer aktiven Spielsession in Echtzeit vorhersagt, ob ein Spieler das Level erfolgreich abschließen wird (Will_Finish = 1) oder das Spiel abbricht (Will_Finish = 0). Das Modell wird als JavaScript-Code in das Spiel exportiert und läuft vollständig client-seitig ohne Server-Kommunikation.

---

## Das Spiel: JumpOne

JumpOne ist ein 2D-Jump-and-Run-Spiel, entwickelt in TypeScript mit dem Phaser-Framework. Spieler bewegen eine Figur durch ein Level voller Hindernisse. Das Spielprinzip basiert auf Sprung-Timing, Plattform-Navigation und wiederholtem Versuch nach Fehlern (Fail-and-Retry).

**Spielzustände:**
- `Playing` – aktive Spielsession
- `Finished` – Spieler hat das Level erfolgreich abgeschlossen
- `Quit` – Spieler hat das Spiel absichtlich beendet
- `Idle` / `Paused` – Spieler ist inaktiv oder pausiert (nach Bereinigung aus Trainingsdaten entfernt)

---

## Telemetrie-Datenerhebung

Das Spiel sendet alle 200–500 ms einen Telemetrie-Datensatz an eine Supabase-Datenbank. Jeder Datensatz enthält den aktuellen Spielzustand als Momentaufnahme.

**Erhobene Features pro Zeile:**

| Feature | Typ | Beschreibung |
|---|---|---|
| `session_id` | String | Eindeutige ID pro Spielsitzung |
| `pos_x`, `pos_y` | Float | Aktuelle Position der Spielfigur |
| `vel_x`, `vel_y` | Float | Geschwindigkeitsvektor |
| `velocity_magnitude` | Float | Gesamtgeschwindigkeit |
| `input_left`, `input_right`, `input_jump` | Boolean | Aktive Tastatureingaben |
| `state` | String | Aktueller Spielzustand |
| `timestamp` | Integer | Spielzeit in Millisekunden |
| `jumpSuccessRate` | Float | Anteil erfolgreicher Sprünge (0–1) |
| `jumpsFailed` | Integer | Anzahl gescheiterter Sprünge |
| `totalFalls` | Integer | Gesamtanzahl der Stürze |
| `avgFallDistance` | Float | Durchschnittliche Fallhöhe |
| `maxFallDistance` | Float | Maximale Fallhöhe |
| `distancePerJump` | Float | Zurückgelegte Strecke pro Sprung |
| `avgTimeBetweenJumps` | Float | Durchschnittliche Pause zwischen Sprüngen (ms) |
| `totalJumpsAttempted` | Integer | Gesamtanzahl Sprungversuche |
| `sessionDuration_sec` | Float | Sessiondauer in Sekunden |
| `totalFalls` | Integer | Gesamtanzahl der Stürze |

---

## Datensatz-Beschreibung (nach Bereinigung)

**Rohdaten (Supabase-Export):**
- Format: PostgreSQL INSERT-Statements (.sql-Datei)
- Ursprüngliche Zeilenzahl: ~126.000 Zeilen aus 23 Sessions

**Datenbereinigungs-Pipeline:**

1. **Entfernung der dominanten Idle-Session** (`1774209321205-sgs17rrl7`): 42.341 Einträge (33% der Daten) mit ausschließlichem `Idle`-State – würde Modell massiv verzerren.
2. **Entfernung einer großen Paused-Session** (`1776803425316-eqi1koup9`): 16.980 Einträge (20% nach Schritt 1), State = `Paused`.
3. **Entfernung einer weiteren Idle-Session** (`1776681488292-gnbskm3md`): 13.021 Einträge (15%), State = `Idle`.

**Begründung:** Sessions die nicht mit `Finished` oder `Quit` enden, repräsentieren kein vollständiges Spielverhalten. Ihr überproportionaler Anteil würde das Modell in Richtung „inaktives Spielverhalten" verzerren.

**Finaler bereinigter Datensatz:**
- **Sessions:** 19
- **Gesamtzeilen:** 53.659
- **Trainingszeilen** (nach Entfernung der Outcome-States): 53.647
- **Klassenverteilung:** Will_Finish=1: 31.877 Zeilen (59.4%), Will_Finish=0: 21.770 Zeilen (40.6%)
- **Sessions mit Finished-Outcome:** 6 von 19 (31.6%)

---

## Feature Engineering & Preprocessing

**Label-Vergabe (Propagation):**  
Das Label `Will_Finish` wird nicht pro Zeile gesetzt, sondern pro Session: Wenn *irgendeine* Zeile einer Session den State `Finished` hat, erhalten *alle* Zeilen dieser Session den Label `1`. Alle anderen erhalten `0`. Danach werden die `Finished`- und `Quit`-Zeilen selbst aus dem Training entfernt (sie repräsentieren den Outcome, nicht das Spielverhalten).

**Subsampling (optional):**  
Mit `--max-rows N` kann die Anzahl Trainingszeilen pro Session begrenzt werden, um zu verhindern dass große Sessions das Modell dominieren.

**Features für Training (10 Features):**

| Feature | Importance (XGBoost Gain) |
|---|---|
| `avgTimeBetweenJumps` | **30.4%** |
| `pos_y` | **21.2%** |
| `maxFallDistance` | 12.3% |
| `jumpSuccessRate` | 12.3% |
| `totalFalls` | 7.9% |
| `distancePerJump` | 7.7% |
| `totalJumpsAttempted` | 4.2% |
| `jumpsFailed` | 4.1% |
| `velocity_magnitude` | 0.0% |
| `pos_x` | 0.0% |

**Interpretation der Top-Features:**
- `avgTimeBetweenJumps` (30.4%): Der wichtigste Prädiktor. Spieler die das Spiel abbrechen, springen langsamer/zögerlicher oder machen längere Pausen (Frustration). Sehr reaktive Spieler gewinnen häufiger.
- `pos_y` (21.2%): Die vertikale Position ist entscheidend – Spieler die sich dauerhaft in hohen Bereichen des Levels aufhalten, schließen eher ab.
- `maxFallDistance` und `jumpSuccessRate` (je 12.3%): Skill-Indikatoren. Niedrige Fallhöhe und hohe Sprung-Erfolgsrate korrelieren stark mit Spielabschluss.

---

## Modell-Vergleich

Drei Modelle wurden trainiert und verglichen:

| Modell | Accuracy | F1-Score | AUC-ROC |
|---|---|---|---|
| Logistic Regression (Baseline) | 86.0% | 0.888 | 0.874 |
| Decision Tree (max_depth=4) | 92.8% | 0.941 | 0.974 |
| **XGBoost (30 Bäume, depth=3)** | **95.9%** | **0.966** | **0.997** |

**XGBoost Hyperparameter:**
- `n_estimators`: 30 (Anzahl Bäume)
- `max_depth`: 3 (flache Bäume für kleinere JS-Exportgröße)
- `learning_rate`: 0.1
- `base_score`: 0.5 (explizit gesetzt für m2cgen-Kompatibilität)

**Train/Test-Split:** 80%/20%, stratifiziert, `random_state=42`

**Warum XGBoost?**
- Gradient Boosting kombiniert viele schwache Lerner sequenziell
- Robuster gegenüber nicht-normalverteilten Features (relevant da viele Features wie `jumpsFailed`, `totalFalls` rechtsschief sind)
- Viel bessere Trennschärfe (AUC 0.997 vs. 0.874) bei gleichzeitig kompaktem Modell (16.276 Zeichen JS-Code)

---

## Verteilung der Features (Gaussian-Analyse)

Normalverteilungstest (D'Agostino K²-Test) auf aggregierten Session-Daten:

| Feature | Normalverteilt? | Skewness | Kurtosis |
|---|---|---|---|
| `velocity_magnitude` | ✅ Ja (p=0.897) | -0.112 | -0.651 |
| `avgFallDistance` | ✅ Ja (p=0.259) | -0.758 | -0.421 |
| `maxFallDistance` | ✅ Ja (p=0.323) | -0.414 | -1.005 |
| `jumpSuccessRate` | ❌ Nein (p<0.001) | -2.561 | 6.899 |
| `jumpsFailed` | ❌ Nein (p<0.001) | 2.171 | 4.333 |
| `totalFalls` | ❌ Nein (p<0.001) | 1.798 | 2.650 |
| `distancePerJump` | ❌ Nein (p<0.001) | -3.598 | 12.823 |
| `avgTimeBetweenJumps` | ❌ Nein (p<0.001) | 3.259 | 10.583 |
| `totalJumpsAttempted` | ❌ Nein (p<0.001) | 2.019 | 4.028 |

**PCA Skill Score (PC1):**
- Erklärt 48.5% der Gesamtvarianz über alle 10 Features
- Ist selbst normalverteilt (p = 0.80) – der kombinierte Skill-Score der Spieler folgt einer Gauß-Verteilung
- Interpretation: Beendete Sessions (Will_Finish=1) haben tendenziell höhere PC1-Scores

**Relevanz für XGBoost:** Tree-basierte Modelle sind distributions-agnostisch – die Nicht-Normalverteilung einzelner Features stellt kein Problem dar. Für lineare Modelle (Logistic Regression) hingegen wären Transformationen (z.B. log-Transformation für `avgTimeBetweenJumps`) sinnvoll.

---

## Integration in das Spiel

**Export-Prozess:**
Das XGBoost-Modell wird mit der Bibliothek `m2cgen` (Model to Code Generator) als reiner JavaScript-Code exportiert. Dieser Code enthält das vollständige Modell als verschachtelte If-Else-Bedingungen und Array-Operationen.

**Verwendung in TypeScript (WinPredictor.ts):**
```typescript
// Generierter Code wird importiert und aufgerufen mit:
const features = [
    jumpSuccessRate, jumpsFailed, totalFalls, maxFallDistance,
    distancePerJump, avgTimeBetweenJumps, totalJumpsAttempted,
    velocity_magnitude, pos_x, pos_y
];
const winProbability = score(features); // gibt Wert zwischen 0 und 1 zurück
```

Das Modell wird jede Sekunde aufgerufen und zeigt dem Spieler oder dem Entwickler die aktuelle Gewinnwahrscheinlichkeit an.

**Modellgröße:** 16.276 Zeichen (im Vergleich: Decision Tree 1.240, Logistic Regression 384)

---

## Technische Pipeline (Skripte)

| Skript | Funktion |
|---|---|
| `session_overview.py` | Übersicht über Sessions; `--delete`, `--clean` für Datenbereinigung |
| `ml_pipeline/data_parser.py` | Parst .sql-Datei → pandas DataFrame; robust gegenüber beiden SQL-Formaten |
| `ml_pipeline/train_xgboost.py` | Trainiert LR, DT, XGBoost; exportiert nach `WinPredictor.ts` |
| `ml_pipeline/gaussian_check.py` | Normalverteilungstest + Plots für alle Features |
| `ml_pipeline/overall_skill_distribution.py` | PCA-Skill-Score-Analyse und Visualisierung |
| `ml_pipeline/visualize_results.py` | Erzeugt alle 8 Publikations-Plots unter `ml_pipeline/plots/` |

---

## Grenzen und Ausblick

**Aktuelle Limitierungen:**
- **Kleine Stichprobe:** Nur 19 Sessions für Training sind sehr wenig für generalisierende Aussagen. Die hohen Metriken (~96% Accuracy) könnten partiell auf Overfitting an bekannte Spieler-Muster zurückzuführen sein.
- **Nur ein Level:** Das Modell ist level-spezifisch trainiert und muss bei neuen Levels neu trainiert werden.
- **Keine Cross-Validation:** Aktuell nur ein einziger Train/Test-Split. K-Fold-Kreuzvalidierung wäre robuster.
- **Klassen-Imbalance auf Session-Ebene:** 6 von 19 Sessions sind positiv (Finished), was die Session-Ebene stark unbalanciert macht.

**Mögliche Erweiterungen:**
- Mehr Spieler-Sessions sammeln für robusteres Modell
- `scale_pos_weight` in XGBoost für bessere Klassen-Balancierung
- SHAP-Werte für interpretierbare Vorhersage-Erklärungen
- Separates Modell pro Level oder Transfer Learning bei neuem Level
- Online-Learning: Modell aktualisiert sich mit jeder neuen Session

---

## Verwendete Bibliotheken

| Bibliothek | Version | Zweck |
|---|---|---|
| `xgboost` | 2.x | Gradient Boosting Classifier |
| `scikit-learn` | 1.x | Preprocessing, Baseline-Modelle, Metriken |
| `m2cgen` | 0.10 | Modell → JavaScript/TypeScript Export |
| `pandas` | 2.x | Datenverarbeitung |
| `scipy` | 1.x | Normalverteilungstest (D'Agostino) |
| `matplotlib` / `seaborn` | aktuell | Visualisierungen |
| `Phaser` | 3.x | Game Framework (TypeScript) |
| `Supabase` | aktuell | PostgreSQL Backend / Telemetrie-Datenbank |
