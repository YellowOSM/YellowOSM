<div style="display:flex; flex-direction:column; justify-content:center">
<a href="https://yellowosm.com/"><img src="imgs/YOSM_square_200.png" /></a>
<h1 style="text-transform:none">YellowOSM</h1></div><!-- .slide: data-background-image="imgs/bg1.jpg" -->


# Warum?


### Schon bei OSM nach "Friseur" gesucht?
<img src="imgs/ff_friseur.png">


# Warum?
* OpenStreetMap ist weltweit größte freie Geodatenbank
* zahlreiche Interfaces dafür, aber oft schwer zu bedienen
* auf mobilen Geräten teilweise nicht verfügbar


# Warum?
* keine freie & offene Alternative zu Google, Herold etc.
  * v.A. für Geschäfte & Dienstleistende
* undemokratisch
  * wenige Institutionen bestimmen was alle sehen
  * Werbung
  * Monopolstellung
* teilweise langsam bei Aktualisierung


## Der "umbenannt worden" Ring
<a href="https://blog.flo.cx/2012/07/der-umbenannt-worden-ring/" target="blank">
  https://blog.flo.cx/2012/07/der-umbenannt-worden-ring/</a>
<img src="imgs/google_maps_umbenannt_worden.png" />


# Unsere Ziele
* Daten aus OSM allen leichter zugänglich machen
  * einfach zu bedienendes Interface
* Bearbeiten & Hinzufügen vereinfachen
  * durch den <i>Wisdom of the Crowd</i> besser werden
  * demokratischer
  * uneinholbar voran, vgl. Wikipedia, StackOverflow
* Vermeiden von Tracking


<div style="display:flex; flex-direction:column; justify-content:center">
<a href="https://yellowosm.com/"><img src="imgs/YOSM_square_200.png" /></a>
<h1 style="text-transform:none">YellowOSM</h1></div><!-- .slide: data-background-image="imgs/bg1.jpg" -->
<h2><a href="https://yellowosm.com/map">Demo Time!</a></h2>


## WebApp
<ul style="float:left">
  <li><a href="https://www.yellowosm.com/map">yellowosm.com</a></li>
  <li>ohne Installation nutzbar</li>
  <li>effizientere Entwicklung</li>
  <li>Fokus auf mobile Geräte</li>
  <li>immer besser unterstützt</li>
</ul>

<img src="imgs/screenshots/mobile.png" style="width: 30%; height: auto">


## Technik
* Daten von der <a href="https://download.geofabrik.de/europe/austria.html">Geofabrik</a>
* Import in PostgreSQL-Datenbank
* Export für ElasticSearch (Python-Skripts)
* Frontend in Angular
* Integration bestehender Tools:
  * osm2pgsql, OpenLayers, opening_hours.js


## API
* offene API zur freien Verwendung
* **Gebäudeautomatisierung**: Zeige alle jetzt verfügbaren Lieferdienste in 5km Umkreis
* Einbinden in Webseiten, z.B. "Geschäfte in der Nähe"
* Auswertungen, z.B. Standortanalysen


## Analyse: Datenqualität
Fallstudie: Reitschulgasse
<img src="imgs/screenshots/osm.png">


## Datenqualität: Reitschulgasse
<img src="imgs/reitschulgasse/reitschulgasse.jpg">


## Datenqualität: Reitschulgasse
44 Geschäfte, Friseure, Cafés, Ärzte, Psychologen & co.

Wie viele gibt es auf der Karte?

<img src="imgs/reitschulgasse/chart1.png">


## Datenqualität: Reitschulgasse
Wie viele haben die richtigen Infos?

<a href="https://docs.google.com/spreadsheets/d/1R_Lc-ohfHCeDjvFcl7URPGMyoKAfwOKJbz3Uyq4M2go/edit?usp=sharing">Spreadsheet</a>

<img src="imgs/reitschulgasse/chart2.png">


## Verbesserungen
* Crawling von Websites, Ergänzen der Daten, Machine Learning
* Bearbeiten mobil einfacher machen (OSM-ID-Editor)
* MapRoulette


## MapRoulette
<a href="https://maproulette.org/challenge/4206/">MapRoulette-Challenge</a>

<img src="imgs/maproulette.png">


## Ausblick
* Feedback einholen
* UX verbessern
* Browsing
* Datenqualität verbessern
* Projekt nachhaltig etablieren


### Fun Fact: Warum gibt's in Tirol und Vorarlberg keine Fleischer?


<img src="imgs/ff_fleischerei.png"/>


<img src="imgs/ff_metzger.png"/>


<img src="imgs/ff_butcher.png"/>


## Danke!
<div style="display:flex; align-items:center; justify-content:center;">
<div style="width:200px;"></div>
<a href="https://yellowosm.com/"><img src="imgs/YOSM_square.jpg" /></a>
<i class="twa twa-2x twa-heart" style="margin: 50px;"></i>
<a href="https://netidee.at"><img src="imgs/netidee_logo_projekte.jpg" /></a>
</div>

* <a href="https://yellowosm.com">yellowosm.com</a>
* <a href="https://github.com/YellowOSM/YellowOSM">https://github.com/YellowOSM/YellowOSM</a>
* <a href="https://twitter.com/yellowosm">@yellowosm</a>
* <a href="https://maproulette.org/challenge/4206/">MapRoulette-Challenge</a>
* mit freundlicher Unterstützung durch <a href="https://netidee.at/yellowosm">netidee</a>
