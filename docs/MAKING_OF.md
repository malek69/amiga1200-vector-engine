==============================================================================
  MEDIAN - AMIGA 1200 / THEA1200 AGA PORT [RETAIL VERSION]
  MAKING OF, OPIS PLIKOW ZRODLOWYCH ORAZ PROMPTY DLA AI
==============================================================================
  Oryginal PC : "Median" by Umlaut Design (Windows / PC, 2016)
  Port A1200  : malek69 & Gemini AI (Vibe Coding Edition, listopad 2026)
  Platforma   : Commodore Amiga 1200 (PAL, AGA, 68020+, 2MB Chip + 8MB Fast)
                oraz konsola THEA1200 (przez WHDLoad / Media Access)

------------------------------------------------------------------------------
  1. CO ZOSTALO ZROBIONE, ABY STWORZYC TO DEMO NA AMIGE 1200?
------------------------------------------------------------------------------
  A. Przejecie sprzetu AGA (Bare-Metal Hardware Takeover):
     - Wylaczenie wielozadaniowosci AmigaOS (Forbid/Disable), zachowanie
       oryginalnych wektorow przerwan (VBR), DMA, INTENA oraz Copperlisty.
     - Konfiguracja ekranu PAL 320x256 w 3 bitplanach (8 kolorow, $3200)
       z podwojnym buforowaniem (bpl1/2/3_a <-> bpl1/2/3_b) przelaczanym
       bezposrednio w przerwaniu VBL Level 3 ($6c).

  B. Sprzetowy silnik wektorowy na Blitterze (Hardware Blitter Polygon Engine):
     - Zamiast wolnego rysowania wielokatow przez procesor 68020 piksel po
       pikselu, silnik rysuje tylko jednopikselowe krawedzie metoda XOR (bchg)
       do bufora roboczego scratch_bpl w Chip RAM.
     - Nastepnie uklad Blitter w trybie opadajacym (DESC + Inclusive Fill)
       sprzetowo wypelnia cale wielokaty w jednym przebiegu DMA i naklada je
       na docelowe bitplany (tryb 0: czern/szarosc, tryb 1: wyciecia bialych
       okien, tryb 2: czerwona kula na drugim bitplanie).

  C. Ekstrakcja wektorow HD i matematyczna stabilizacja ksztaltow:
     - Zrodlowe wideo HD (orginal.mp4) zostalo przeanalizowane w natywnej
       rozdzielczosci z zachowaniem idealnych proporcji 1:1 (kwadrat = kwadrat)
       oraz uproszczeniem konturow do czystych 4-wierzcholkowych kwadratow.
     - Czerwone slonce/kula jest dopasowywana matematycznie (minEnclosingCircle)
       do regularnego 32-kata o stalych katach, co calkowicie eliminuje
       falowanie krawedzi podczas ruchu.
     - Wszystkie klatki (30 FPS) zostaly skompresowane poprzez deduplikacje
       identycznych stanow i zapisane w tablicy vec_frame_table.

  D. Dzwiek 16.5 kHz Paula DMA z synchronizacja Audio <-> Wideo (0 ms rozjazdu):
     - Sciezka dzwiekowa zostala przekonwertowana do 8-bitowego PCM (16497 Hz,
       AUD0PER = 215) z filtrem dolnoprzepustowym i limiterem dynamiki.
     - Odtwarzanie obsluguje sprzetowe przerwanie Audio Level 4 ($70) na
       wszystkich 4 kanalach ukladu Paula z podwojnym buforem 2048 bajtow.
     - Glowna petla wideo wylicza numer klatki bezposrednio z licznika
       odtworzonych bajtow audio (pcm_played), dzieki czemu obraz i dzwiek
       sa zablokowane 1:1 przez caly czas trwania dema.

  E. Wlasny WHDLoad Slave (.slave) i paczka .lha dla THEA1200:
     - Napisany od zera w asemblerze M68020 program rozruchowy MedianA1200.slave
       laduje i relokuje wszystkie sekcje (code, pcmdata, chipdata) bez
       potrzeby uzywania Kickstartu w pamieci, umozliwiajac uruchomienie dema
       jednym kliknieciem z pendrive USB na THEA1200 oraz w FS-UAE.

------------------------------------------------------------------------------
  2. OPIS PLIKOW W KATALOGU ~/median-a1200-retail
------------------------------------------------------------------------------
  * MEDIAN_A1200
      Gotowy, skompilowany plik wykonywalny AmigaDOS (format Hunk). Mozna go
      uruchomic bezposrednio z AmigaShell / CLI lub z dyskietki/dysku twardego.

  * MedianA1200_THEA1200_Retail.lha
      Kompletna paczka WHDLoad (Level-1 LHA z ikonami AmigaOS .info oraz
      MedianA1200.slave) przygotowana specjalnie dla konsoli THEA1200 (USB
      Media Access) oraz emulatora FS-UAE Launcher.

  * ud_mdn_a1200_retail.zip
      Paczka wydawnicza w standardzie demoscenowym zawierajaca komentarz ZIP
      (file_id.diz), plik informacyjny, dokumentacje, binarke oraz .lha.

  * main.s
      Glowny modul programu w asemblerze M68020: punkt wejscia, petla glowna
      zsynchronizowana z licznikiem probek audio (pcm_played), tablica
      odwrotnosci inv_tab oraz definicje sekcji code, pcmdata i chipdata.

  * gfx_engine.i
      Obsluga chipsetu AGA: przejecie i przywrocenie systemu (sys_takeover /
      sys_restore), dynamiczna Copperlista, podwojne buforowanie 3 bitplanow
      oraz zmiana odcieni szarosci w rejestrze COLOR01.

  * vec3d_engine.i
      Sprzetowy rasteryzator wielokatow N-katnych wykorzystujacy Blitter
      (rysowanie krawedzi XOR + sprzetowe wypelnianie obszarow + wycinanie
      otworow logicznych).

  * scene_player.i
      Odtwarzacz klatek wektorowych: odczytuje wskaznik klatki z tablicy
      vec_frame_table, ustawia kolor sceny i wywoluje rasteryzator wielokatow.

  * scene_data.i
      Skompilowane dane wektorowe wszystkich klatek dema (tablica wskaznikow
      vec_frame_table oraz lista wspolrzednych wierzcholkow wielokatow).

  * audio_player.i
      Sterownik ukladu dzwiekowego Paula: konfiguracja 4 kanalow DMA (215
      okres = 16497 Hz), obsluga przerwania Level 4 ($70) i licznik pcm_played.

  * median_audio.raw
      Surowy strumien dzwiekowy 8-bit signed PCM (16497 Hz) dolaczany do
      sekcji pcmdata podczas kompilacji asemblerem vasm.

  * file_id.diz / median_a1200_retail.nfo / README_MAKING_OF.txt
      Pliki opisowe dema, dokumentacja techniczna oraz zestaw promptow AI.

------------------------------------------------------------------------------
  3. PROMPTY DLA AI (DO ODTWORZENIA LUB ROZBUDOWY DEMA W VIBE CODING)
------------------------------------------------------------------------------
  [PROMPT 1 - Ekstrakcja wektorow HD i audio z wideo PC -> Asembler M68020]
  "Napisz skrypt w Pythonie (OpenCV + NumPy + FFmpeg), ktory wyciagnie z pliku
   wideo 30 FPS sciezke dzwiekowa 8-bit signed PCM 16497 Hz (z filtrem
   lowpass 7800 Hz i limiterem) oraz strumien zamknietych wielokatow N-katnych
   w rozdzielczosci Amigi 320x256 z zachowaniem proporcji 1:1. Kwadraty
   uprosc algorytmem Douglas-Peucker do 4 wierzcholkow, otwory wewnetrzne
   oznacz jako tryb wycinania (HIERARCHY depth & 1), a czerwone okregi
   dopasuj matematycznie (minEnclosingCircle) do stalego 32-kata. Wygeneruj
   plik scene_data.i w skladni asemblera Motorola (vasm) z deduplikacja klatek."

  [PROMPT 2 - Sprzetowy silnik wypelniania wielokatow na Blitterze Amigi 1200]
  "Napisz w asemblerze M68020 (vasmm68k_mot) kompletny silnik wektorowy dla
   Amigi 1200 (AGA, 320x256 PAL, 3 bitplany, double-buffering). Rysuj krawedzie
   wielokatow metoda XOR (bchg) do bufora roboczego scratch_bpl w Chip RAM,
   a nastepnie wypelniaj prostokat otaczajacy (bounding box) sprzetowo
   ukladem Blitter w trybie DESC + Inclusive Fill ($000a) i nakladaj na
   bitplany w 3 trybach: OR na BPL1, ~A & C (wyciecie otworu) na BPL1 oraz
   OR na BPL2."

  [PROMPT 3 - Dzwiek Paula DMA IRQ Level 4 i synchronizacja Audio <-> Wideo]
  "Napisz sterownik audio w asemblerze M68020 dla ukladu Paula (4 kanaly DMA,
   AUD0PER=215, podwojny bufor 2048 bajtow w Chip RAM) obslugiwany sprzetowym
   przerwaniem Audio Level 4 ($70). W przerwaniu zliczaj odtworzone bajty
   do zmiennej pcm_played, a w petli glownej wyliczaj numer klatki wideo
   (cur_frame = pcm_played * 10 / 5499), aby obraz byl idealnie zablokowany
   z muzyka przez cale demo."

  [PROMPT 4 - Wlasny WHDLoad Slave (.slave) i paczka .lha dla THEA1200]
  "Napisz od zera w asemblerze M68020 plik WHDLoad Slave (WHDLOADS v17,
   ws_KickSize=0, bez wymaganego obrazu Kickstartu), ktory za pomoca
   resload_LoadFile wczyta plik wykonywalny AmigaDOS Hunk, przydzieli sekcje
   CHIP i FAST, wykona 32-bitowa relokacje HUNK_RELOC32, wywola
   resload_FlushCache (offset 64) i uruchomi demo. Nastepnie spakuj projekt
   do archiwum LHA Level-1 z ikonami AmigaOS (.info) pod konsole THEA1200."
==============================================================================
