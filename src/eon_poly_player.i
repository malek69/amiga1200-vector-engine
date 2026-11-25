; ============================================================================
; AETHER FALCON: VANGUARD - Silnik scen wektorowych N-gon (16.16 + move.l)
; Styl: Another World / Delphine Software (Amiga 1200 AGA 256 kolorow)
; ============================================================================
        section code,code

; ----------------------------------------------------------------------------
; af_aw_fill_ngon
; Wypelnia dowolny wielokat wypukly N-gon (3..16 wierzcholkow) wachlarzem
; Wejscie: a0 -> [count.w, x0.w, y0.w, x1.w, y1.w, ...], d6.b = indeks koloru
; ----------------------------------------------------------------------------
        cnop    0,4
af_aw_fill_ngon:
        movem.l d0-d7/a0-a1,-(sp)
        move.w  (a0)+,d7                ; liczba wierzcholkow N
        subq.w  #3,d7                   ; liczba trojkatow = N - 2
        blt.s   .ng_done
        move.w  (a0)+,d0                ; x0 (wierzcholek kotwicy wachlarza)
        move.w  (a0)+,d1                ; y0
        move.l  a0,a1
.ng_lp: move.w  (a1),d2                 ; xi
        move.w  2(a1),d3                ; yi
        move.w  4(a1),d4                ; x(i+1)
        move.w  6(a1),d5                ; y(i+1)
        bsr.s   af_aw_fill_tri
        addq.l  #4,a1
        dbf     d7,.ng_lp
.ng_done:
        movem.l (sp)+,d0-d7/a0-a1
        rts

; ----------------------------------------------------------------------------
; af_aw_fill_tri
; Szybki rasteryzer trojkatow 16.16 fixed-point z zapisem 32-bit move.l
; Wejscie: d0.w=x0, d1.w=y0, d2.w=x1, d3.w=y1, d4.w=x2, d5.w=y2, d6.b=kolor
; ----------------------------------------------------------------------------
        cnop    0,4
af_aw_fill_tri:
        movem.l d0-d7/a0-a4,-(sp)
        ; Sortowanie wierzcholkow wzgledem Y: y0 <= y1 <= y2
        cmp.w   d1,d3
        bge.s   .s01
        exg     d0,d2
        exg     d1,d3
.s01:   cmp.w   d3,d5
        bge.s   .s12
        exg     d2,d4
        exg     d3,d5
        cmp.w   d1,d3
        bge.s   .s12
        exg     d0,d2
        exg     d1,d3
.s12:   move.w  d5,d7
        sub.w   d1,d7                   ; total_dy = y2 - y0
        ble.w   .tri_done

        ; Zapisz posortowane (x0, y0, x1, y1, x2, y2) na stosie:
        ; [sp+0]=x0, [sp+2]=y0, [sp+4]=x1, [sp+6]=y1, [sp+8]=x2, [sp+10]=y2
        move.w  d5,-(sp)
        move.w  d4,-(sp)
        move.w  d3,-(sp)
        move.w  d2,-(sp)
        move.w  d1,-(sp)
        move.w  d0,-(sp)

        ; Rozszerz kolor d6.b na 32 bity (4 piksele naraz)
        and.l   #$ff,d6
        move.l  d6,d0
        lsl.w   #8,d0
        or.w    d0,d6
        move.w  d6,d0
        swap    d6
        move.w  d0,d6
        move.l  d6,a4                   ; a4 = 4x kolor

        lea     recip_table_32,a3
        cmp.w   #512,d7
        ble.s   .dy1
        move.w  #512,d7
.dy1:   move.l  (a3,d7.w*4),d0
        move.w  8(sp),d6
        sub.w   (sp),d6
        ext.l   d6
        muls.l  d0,d6

        move.w  (sp),d4
        swap    d4
        move.w  #$8000,d4               ; cur_x_long (d4.l)

        move.w  2(sp),d1                ; aktualny Y = y0
        lea     chunky_buf,a0
        move.w  d1,d7
        mulu.w  #320,d7
        add.l   d7,a0

        ; --- GORNA POLOWKA: y0 .. y1-1 ---
        move.w  6(sp),d7                ; y1
        sub.w   2(sp),d7                ; - y0
        ble.s   .do_bot

        cmp.w   #512,d7
        ble.s   .dy2
        move.w  #512,d7
.dy2:   move.l  (a3,d7.w*4),d2
        move.w  4(sp),d0
        sub.w   (sp),d0
        ext.l   d0
        muls.l  d2,d0

        move.w  (sp),d2                 ; x0
        swap    d2
        move.w  #$8000,d2               ; cur_x_short (d2.l)
        subq.w  #1,d7
.top_lp:
        bsr.s   .draw_span
        add.l   d6,d4
        add.l   d0,d2
        lea     320(a0),a0
        addq.w  #1,d1
        dbf     d7,.top_lp

.do_bot:
        ; --- DOLNA POLOWKA: y1 .. y2-1 ---
        move.w  10(sp),d7               ; y2
        sub.w   6(sp),d7                ; - y1
        ble.s   .tri_pop

        move.w  8(sp),d0                ; x2
        move.w  4(sp),d2                ; x1
        sub.w   d2,d0                   ; x2 - x1
        swap    d0
        clr.w   d0
        divs.l  d7,d0                   ; step_short_bot (d0.l)

        swap    d2
        move.w  #$8000,d2               ; cur_x_short (d2.l)
        subq.w  #1,d7
.bot_lp:
        bsr.s   .draw_span
        add.l   d6,d4
        add.l   d0,d2
        lea     320(a0),a0
        addq.w  #1,d1
        dbf     d7,.bot_lp

.tri_pop:
        lea     12(sp),sp
.tri_done:
        movem.l (sp)+,d0-d7/a0-a4
        rts

.draw_span:
        tst.w   d1
        blt.s   .sp_ret
        ifd FULL_RES
        cmp.w   #255,d1
        else
        cmp.w   #127,d1
        endif
        bgt.s   .sp_ret

        move.l  d4,d3
        swap    d3                      ; xl
        move.l  d2,d5
        swap    d5                      ; xr
        cmp.w   d3,d5
        bge.s   .sp_ord
        exg     d3,d5
.sp_ord:
        tst.w   d5
        blt.s   .sp_ret
        cmp.w   #319,d3
        bgt.s   .sp_ret
        tst.w   d3
        bge.s   .sp_cl
        moveq   #0,d3
.sp_cl:
        cmp.w   #319,d5
        ble.s   .sp_cr
        move.w  #319,d5
.sp_cr:
        lea     (a0,d3.w),a1
        sub.w   d3,d5                   ; szerokosc - 1
        move.l  a4,d3                   ; 4 bajty koloru
        move.w  d5,a2
        lsr.w   #2,d5
        beq.s   .sp_rem
        subq.w  #1,d5
.sp_l4:
        move.l  d3,(a1)+                ; szybki zapis 4 pikseli naraz
        dbf     d5,.sp_l4
.sp_rem:
        move.w  a2,d5
        and.w   #3,d5
.sp_l1:
        move.b  d3,(a1)+
        dbf     d5,.sp_l1
.sp_ret:
        rts

; ----------------------------------------------------------------------------
; ============================================================================
; af_play_eon_scene - Rotoskopowy odtwarzacz wielotonowych wielokatow Eon (TBL)
; Wejscie: a2 -> lista [color.w, count.w, x0.w, y0.w, ...], d4.w = dx, d5.w = dy
; ============================================================================
        cnop    0,4
af_play_eon_scene:
        movem.l d0-d7/a0-a2,-(sp)
.eon_lp:move.w  (a2)+,d6                ; kolor wielokata (-1 = koniec sceny)
        bmi.s   .eon_done
        move.w  (a2)+,d7                ; liczba wierzcholkow N
        lea     af_dyn_poly(pc),a0
        move.w  d7,(a0)+
        subq.w  #1,d7
.eon_v: move.w  (a2)+,d0
        add.w   d4,d0
        move.w  d0,(a0)+
        move.w  (a2)+,d1
        add.w   d5,d1
        ifnd FULL_RES
        asr.w   #1,d1
        endif
        move.w  d1,(a0)+
        dbf     d7,.eon_v
        lea     af_dyn_poly(pc),a0
        bsr.w   af_aw_fill_ngon
        bra.s   .eon_lp
.eon_done:
        movem.l (sp)+,d0-d7/a0-a2
        rts

; ----------------------------------------------------------------------------
; af_draw_aw_briefing: Animowany portret Dowodcy + skaner taktyczny (Eon TBL)
; ----------------------------------------------------------------------------
        cnop    0,4
af_draw_aw_briefing:
        movem.l d0-d7/a0-a2,-(sp)
        ; Plynny ruch oddechu i gestu Dowodcy w rytm vbl_tick
        move.l  vbl_tick(pc),d0
        lsr.l   #3,d0
        and.w   #7,d0
        move.w  d0,d5
        cmp.w   #4,d5
        ble.s   .br_dy1
        neg.w   d5
        addq.w  #8,d5
.br_dy1:subq.w  #2,d5                   ; d5 = -2..+2 px
        moveq   #0,d4
        lea     eon_commander_scene(pc),a2
        bsr.w   af_play_eon_scene
        ; Animowana fala energetyczna / hologram na dloni Dowodcy
        move.l  vbl_tick(pc),d3
        lsr.l   #2,d3
        and.w   #7,d3
        addq.w  #3,d3
        move.w  #202,d0
        ifd FULL_RES
        move.w  #122,d1
        else
        moveq   #61,d1
        endif
        add.w   d5,d1
        move.b  #253,d6
        jsr     af_fill_chunky_diamond
        movem.l (sp)+,d0-d7/a0-a2
        rts

; ----------------------------------------------------------------------------
; af_draw_aw_debrief: Animowany portret Pilota 3/4 + przelot zwyciestwa (Eon)
; ----------------------------------------------------------------------------
        cnop    0,4
af_draw_aw_debrief:
        movem.l d0-d7/a0-a2,-(sp)
        move.l  vbl_tick(pc),d0
        lsr.l   #4,d0
        and.w   #3,d0
        move.w  d0,d5
        subq.w  #1,d5
        moveq   #0,d4
        lea     eon_pilot_portrait_scene(pc),a2
        bsr.w   af_play_eon_scene
        ; Dynamiczne smugi swiatla w tle (zlote przy zwyciestwie, czerwone przy Game Over)
        move.l  vbl_tick(pc),d0
        lsl.w   #2,d0
        and.w   #255,d0
        add.w   #32,d0
        ifd FULL_RES
        move.w  #44,d1
        else
        moveq   #22,d1
        endif
        moveq   #5,d3
        move.b  #254,d6
        tst.b   af_game_over
        beq.s   .deb_col_ok
        move.b  #252,d6
.deb_col_ok:
        jsr     af_fill_chunky_diamond
        movem.l (sp)+,d0-d7/a0-a2
        rts

; ----------------------------------------------------------------------------
; af_draw_aw_intro: 5-aktowy film otwierajacy w stylu Eon (TBL) + AURA-3D
; ----------------------------------------------------------------------------
        cnop    0,4
af_draw_aw_intro:
        movem.l d0-d7/a0-a5,-(sp)
        move.l  af_state_timer,d7
        cmp.l   #130,d7
        blo.w   af_intro_cut1           ; Akt 1: Salute to the Sky (Eon kadr 1)
        cmp.l   #255,d7
        blo.w   af_intro_cut2           ; Akt 2: Alarm w bazie Solis + dojazd na motorze
        cmp.l   #380,d7
        blo.w   af_intro_cut2b          ; Akt 3: Zblizenie na kabine XF-14 i dopalacze
        cmp.l   #560,d7
        blo.w   af_intro_cut34          ; Akt 4: Start 3D XF-14 Albatros w niebo!
        ; Akt 5 (560+): Gwiezdne niebo + wielotonowy portret Pilota pod tytulem
        moveq   #0,d4
        moveq   #0,d5
        lea     eon_pilot_portrait_scene(pc),a2
        bsr.w   af_play_eon_scene
        bra.w   af_intro_done

af_emit_dyn_poly:
        movem.l d0-d1/a0,-(sp)
        ifnd FULL_RES
        lea     af_dyn_poly(pc),a0
        move.w  (a0)+,d0
        subq.w  #1,d0
.sc_y:  addq.l  #2,a0
        move.w  (a0),d1
        asr.w   #1,d1
        move.w  d1,(a0)+
        dbf     d0,.sc_y
        endif
        lea     af_dyn_poly(pc),a0
        bsr.w   af_aw_fill_ngon
        movem.l (sp)+,d0-d1/a0
        rts

; Akt 1 (0..129): Sylwetka Pilota unoszacego piesc na tle srebrnego nieba (Eon kadr 1)
af_intro_cut1:
        move.w  d7,d4
        lsr.w   #2,d4
        neg.w   d4
        add.w   #22,d4                  ; dynamiczny najazd kamery
        move.w  d7,d5
        lsr.w   #3,d5
        neg.w   d5
        add.w   #12,d5                  ; uniesienie piesci w niebo
        lea     eon_salute_scene(pc),a2
        bsr.w   af_play_eon_scene
        ; Pulsujaca aura Eteru wokol piesci
        move.w  #214,d0
        add.w   d4,d0
        ifd FULL_RES
        move.w  #44,d1
        else
        moveq   #22,d1
        endif
        add.w   d5,d1
        move.w  d7,d3
        lsr.w   #2,d3
        and.w   #7,d3
        addq.w  #3,d3
        move.b  #253,d6
        jsr     af_fill_chunky_diamond
        bra.w   af_intro_done

; Akt 2 (130..254): Alarm bojowy na lotnisku Solis + dojazd pilota do XF-14
af_intro_cut2:
        moveq   #0,d4
        moveq   #0,d5
        lea     eon_airbase_bg_scene(pc),a2
        bsr.w   af_play_eon_scene
        move.w  d7,d0
        sub.w   #130,d0
        lsl.w   #1,d0
        cmp.w   #185,d0
        ble.s   .mx_ok
        move.w  #185,d0
.mx_ok: addq.w  #8,d0
        ifd FULL_RES
        move.w  #188,d1
        else
        moveq   #94,d1
        endif
        jsr     af_blit_moto_sprite
        ; Pulsujaca syrena alarmowa na wiezy kontroli lotow
        move.w  #52,d0
        ifd FULL_RES
        move.w  #64,d1
        else
        moveq   #32,d1
        endif
        move.w  d7,d3
        and.w   #15,d3
        addq.w  #2,d3
        move.b  #252,d6
        jsr     af_fill_chunky_diamond
        bra.w   af_intro_done

; Akt 3 (255..379): Wielotonowe zblizenie Eon na kabine XF-14 i odpalenie dopalaczy
af_intro_cut2b:
        moveq   #0,d4
        moveq   #0,d5
        lea     eon_airbase_bg_scene(pc),a2
        bsr.w   af_play_eon_scene
        move.w  d7,d4
        sub.w   #255,d4
        asr.w   #2,d4
        neg.w   d4
        moveq   #0,d5
        btst    #1,d7
        beq.s   .shk_ok
        moveq   #-2,d5                  ; wibracja kadluba od dopalaczy!
.shk_ok:lea     eon_cockpit_ignition_scene(pc),a2
        bsr.w   af_play_eon_scene
        ; Pulsujacy plomien z dysz XF-14
        move.w  #308,d0
        add.w   d4,d0
        ifd FULL_RES
        move.w  #138,d1
        else
        moveq   #69,d1
        endif
        move.w  d7,d3
        and.w   #15,d3
        addq.w  #6,d3
        move.b  #254,d6
        jsr     af_fill_chunky_diamond
        bra.w   af_intro_done

; Akt 4 (380..559): Start 3D XF-14 Albatros w niebo z pelnymi smugami i flara!
af_intro_cut34:
        moveq   #0,d4
        moveq   #0,d5
        lea     eon_airbase_bg_scene(pc),a2
        bsr.w   af_play_eon_scene
        jsr     af_clear_fighter_zbuffer
        move.w  #0,cam_ox
        move.w  #0,cam_oy
        move.w  #-155,cam_oz
        clr.w   cam_sin
        move.w  #256,cam_cos
        move.l  af_state_timer,d3
        sub.l   #380,d3
        moveq   #0,d0
        moveq   #-16,d1
        move.w  d3,d2
        asr.w   #1,d2
        cmp.w   #42,d2
        ble.s   .rl_ok
        moveq   #42,d2
.rl_ok: jsr     build_rot_matrix_3d
        move.w  d3,d4
        asr.w   #1,d4
        cmp.w   #110,d4
        ble.s   .jx_ok
        move.w  #110,d4
.jx_ok: move.w  d3,d5
        asr.w   #1,d5
        ifd FULL_RES
        move.w  #28,d1
        sub.w   d5,d1
        cmp.w   #-64,d1
        bge.s   .jy_ok
        move.w  #-64,d1
        else
        moveq   #14,d1
        asr.w   #1,d5
        sub.w   d5,d1
        cmp.w   #-32,d1
        bge.s   .jy_ok
        move.w  #-32,d1
        endif
.jy_ok: move.w  d1,d5
        move.w  d3,d6
        lsl.w   #2,d6
        add.w   #12,d6
        movem.w d4-d6,-(sp)
        lea     xf14_verts,a0
        lea     v2_proj_buf,a1
        move.w  #xf14_vert_count,d7
        jsr     transform_and_project_verts
        lea     xf14_norms,a0
        lea     v2_env_buf,a1
        move.w  #xf14_vert_count,d7
        jsr     transform_normals_envmap
        lea     xf14_env_mesh,a0
        lea     v2_proj_buf,a1
        lea     v2_tex_bank,a2
        lea     v2_env_buf,a3
        jsr     draw_gouraud_env_mesh_v2
        movem.w (sp)+,d4-d6
        cmp.w   #320,d6
        bgt.s   af_intro_done
        jsr     ptrail_emit_twin_nozzles
        jsr     ptrail_update_and_draw
af_intro_done:
        movem.l (sp)+,d0-d7/a0-a5
        rts

        even
; --- KADR 1 EON (TBL): Sylwetka pilota z uniesiona piescia na srebrnym niebie ---
; --- TLO BAZY SOLIS W STYLU EON (TBL): Bez bitmapy, czyste wielotonowe wielokaty ---
eon_airbase_bg_scene:
        dc.w    16,  4,  -10,-10, 330,-10, 330,142, -10,142   ; nocne niebo Eon (#16)
        dc.w    22,  5,  -10,142,  80,104, 175,122, 265,98, 330,142 ; gory w tle (#22)
        dc.w    24,  4,   28,142,  36,84,  68,84,  76,142     ; wieza kontroli lotow (#24)
        dc.w    253, 4,   34,88,   70,88,  70,96,  34,96      ; turkusowa szyba wiezy (#253)
        dc.w    23,  4,   92,142, 108,116, 178,116, 192,142   ; hangar eskadry Vanguard (#23)
        dc.w    215, 4,  118,142, 124,124, 162,124, 168,142   ; swiatlo z otwartego hangaru
        dc.w    20,  4,  -10,142, 330,142, 330,265, -10,265   ; plyta lotniska (#20)
        dc.w    254, 4,  -10,142, 330,142, 330,145, -10,145   ; zlota linia horyzontu Solis (#254)
        dc.w    215, 4,  154,145, 166,145, 196,265, 124,265   ; turkusowy pas startowy
        dc.w    -1

eon_salute_scene:
        dc.w    30, 4,  -40,-40, 360,-40, 360,295, -40,295   ; srebrzyste niebo Eon
        dc.w    215, 5,  46,174, 88,128, 124,116, 118,136, 62,196
        dc.w    217, 4, 124,116, 174,80, 184,92, 132,126
        dc.w    215, 4, 174,80, 198,42, 214,48, 186,92
        dc.w    24,  4,  68,118, 92,98, 114,104, 96,124
        dc.w    16, 6,  -16,255, 22,190, 74,138, 118,134, 108,214, 72,255
        dc.w    16, 6,   78,128, 72,94, 88,72, 116,74, 126,96, 114,126
        dc.w    16, 4,  112,134, 178,86, 192,102, 124,154
        dc.w    16, 5,  176,88, 196,46, 228,38, 246,66, 212,104
        dc.w    16, 4,   18,192, 54,186, 48,255, -16,255
        dc.w    -1

; --- KADR 2 EON (TBL): Portret Dowodcy eskadry opartego na dloni (Briefing) ---
eon_commander_scene:
        dc.w    16, 4,  -10,-10, 330,-10, 330,265, -10,265
        dc.w    215, 5,  156,154, 216,136, 319,144, 319,255, 168,255
        dc.w    253, 4,  268,142, 319,138, 319,192, 286,184
        dc.w    215, 4,  148,186, 174,164, 194,255, 152,255
        dc.w    22,  5,  196,112, 246,108, 258,158, 218,166, 192,142
        dc.w    24,  5,  182,54, 216,42, 254,56, 260,112, 206,124
        dc.w    123, 6,  186,62, 218,48, 242,64, 238,114, 206,122, 184,96
        dc.w    125, 5,  192,66, 214,56, 226,84, 212,114, 188,94
        dc.w    30,  4,  194,72, 206,68, 208,94, 192,90
        dc.w    16,  5,  188,42, 232,36, 264,58, 256,96, 238,68
        dc.w    16,  4,  190,74, 208,72, 206,79, 190,79
        dc.w    123, 5,  188,122, 224,116, 236,154, 204,196, 184,162
        dc.w    125, 4,  192,122, 204,120, 202,172, 188,168
        dc.w    30,  4,  206,120, 216,120, 214,166, 204,166
        dc.w    125, 4,  218,122, 228,124, 224,158, 215,158
        dc.w    -1

; --- KADR 3 EON (TBL): Portret Pilota 3/4 z bocznym swiatlem (Debriefing) ---
eon_pilot_portrait_scene:
        dc.w    16, 4,  -10,-10, 330,-10, 330,265, -10,265
        dc.w    215, 5,   64,196, 118,176, 146,192, 138,255,  46,255
        dc.w    215, 5,  208,184, 266,174, 308,208, 316,255, 218,255
        dc.w    253, 4,  248,182, 294,198, 286,246, 242,232
        dc.w    23,  6,  104,48, 152,24, 204,42, 214,108, 174,148, 114,116
        dc.w    25,  5,  112,56, 156,34, 182,66, 154,112, 114,96
        dc.w    25,  4,   74,108, 102,96, 108,118, 82,126
        dc.w    123, 6,  136,74, 176,56, 204,88, 214,158, 188,188, 148,144
        dc.w    125, 5,  154,68, 184,64, 202,106, 198,174, 168,154
        dc.w    30,  4,  174,72, 192,82, 204,142, 186,164
        dc.w    16,  4,  128,78, 158,68, 162,76, 132,86
        dc.w    16,  4,  134,88, 156,84, 152,96, 136,94
        dc.w    24,  4,  156,102, 172,118, 162,132, 148,124
        dc.w    252, 4,  156,144, 182,142, 178,154, 158,152
        dc.w    -1

; --- KADR 4 EON (TBL): Wielotonowe zblizenie na kabine XF-14 i dysze ---
eon_cockpit_ignition_scene:
        dc.w    30,  5,  120,148, 214,114, 340,114, 340,152, 152,158
        dc.w    24,  4,  152,158, 340,152, 340,178, 186,174
        dc.w    16,  4,  186,174, 340,178, 340,196, 216,188
        dc.w    215, 4,  214,114, 244,82, 296,82, 314,114
        dc.w    253, 4,  248,86, 288,86, 300,110, 232,110
        dc.w    16,  4,  254,94, 274,88, 282,108, 252,108   ; sylwetka pilota w kokpicie
        dc.w    254, 4,  164,132, 224,124, 226,130, 166,136   ; zloty pas eskadry Vanguard
        dc.w    -1

af_dyn_poly:
        ds.w    18

af_draw_vanguard_crest:
        movem.l d0-d6,-(sp)
        ifd FULL_RES
        move.w  #112,d1
        else
        moveq   #54,d1
        endif
        move.w  #160,d0
        move.w  #96,d2
        move.w  d1,d3
        sub.w   #18,d3
        move.w  #160,d4
        move.w  d1,d5
        add.w   #12,d5
        move.b  #$FE,d6
        bsr.w   af_aw_fill_tri
        move.w  #160,d0
        move.w  #224,d2
        move.w  d1,d3
        sub.w   #18,d3
        move.w  #160,d4
        move.w  d1,d5
        add.w   #12,d5
        move.b  #$FE,d6
        bsr.w   af_aw_fill_tri
        move.w  #160,d0
        sub.w   #14,d1
        move.w  #140,d2
        move.w  d1,d3
        add.w   #20,d3
        move.w  #180,d4
        move.w  d3,d5
        move.b  #$FD,d6
        bsr.w   af_aw_fill_tri
        movem.l (sp)+,d0-d6
        rts
