; ============================================================================
;  MODUL: scene_player.i | Amiga 1200 (AGA / 68020+) & THEA1200 Vector Engine v1.0
;  FUNKCJE: play_vector_frame (dekoder strumienia klatek wektorowych i palety Coppera)
; ============================================================================
; ============================================================================
;  PLIK: scene_player.i
;  OPIS MODULU:
;    - Odtwarzacz strumienia klatek wektorowych (play_vector_frame):
;      pobiera wskaznik klatki cur_frame z tablicy vec_frame_table,
;      ustawia kolor COLOR01 i wywoluje rasteryzator dla kazdego wielokata.
; ============================================================================

play_vector_frame:
    move.w  cur_frame(pc),d0
    cmp.w   vec_frame_count(pc),d0
    blo.s   .idx_ok
    move.w  vec_frame_count(pc),d0
    subq.w  #1,d0
.idx_ok:
    lea     vec_frame_table(pc),a0
    move.l  (a0,d0.w*4),a1
    move.w  (a1)+,d0
    bsr.w   set_col01_shade

.prim_loop:
    move.w  (a1)+,d0                ; 0=BPL1 OR, 1=BPL1 CLEAR, 2=BPL2 OR, -1=koniec
    bmi.s   .frame_end
    bsr.w   draw_polygon_mode
    bra.s   .prim_loop

.frame_end:
    rts
