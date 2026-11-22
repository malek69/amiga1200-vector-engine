; ============================================================================
;  PLIK: gfx_engine.i
;  OPIS MODULU:
;    - Przejecie kontroli nad chipsetem AGA (sys_takeover) i powrot do systemu
;      (sys_restore) wraz z zachowaniem VBR, DMACON, INTENA oraz Copperlisty.
;    - Konfiguracja ekranu 320x256 PAL w 3 bitplanach (8 kolorow, $3200)
;      z podwojnym buforowaniem (bpl1/2/3_a <-> bpl1/2/3_b).
;    - Sprzetowy Anti-Aliasing na Blitterze (apply_blitter_aa): przesuniecie
;      o 1 piksel na 3. bitplanie (BPL3) dla wygladzenia skosnych krawedzi.
;    - Dynamiczna zmiana odcieni szarosci w Copperze (set_col01_shade).
; ============================================================================

CUSTOM      equ $dff000
DMACONR     equ $002
INTENA      equ $09a
INTENAR     equ $01c
INTREQR     equ $01e
INTREQ      equ $09c
DMACON      equ $096
BLTCON0     equ $040
BLTCON1     equ $042
BLTAFWM     equ $044
BLTALWM     equ $046
BLTCPTH     equ $048
BLTBPTH     equ $04c
BLTAPTH     equ $050
BLTDPTH     equ $054
BLTSIZE     equ $058
BLTCMOD     equ $060
BLTBMOD     equ $062
BLTAMOD     equ $064
BLTDMOD     equ $066
BLTADAT     equ $074
COP1LC      equ $080
COPJMP1     equ $088
DIWSTRT     equ $08e
DIWSTOP     equ $090
DDFSTRT     equ $092
DDFSTOP     equ $094
BPLCON0     equ $100
BPLCON1     equ $102
BPLCON2     equ $104
BPLCON3     equ $106
BPL1MOD     equ $108
BPL2MOD     equ $10a
FMODE       equ $1fc
COLOR00     equ $180
COLOR01     equ $182
COLOR02     equ $184
COLOR03     equ $186
COLOR04     equ $188
COLOR05     equ $18a
COLOR06     equ $18c
COLOR07     equ $18e
AUD0LCH     equ $0a0
AUD0LEN     equ $0a4
AUD0PER     equ $0a6
AUD0VOL     equ $0a8
AUD1LCH     equ $0b0
AUD1LEN     equ $0b4
AUD1PER     equ $0b6
AUD1VOL     equ $0b8
AUD2LCH     equ $0c0
AUD2LEN     equ $0c4
AUD2PER     equ $0c6
AUD2VOL     equ $0c8
AUD3LCH     equ $0d0
AUD3LEN     equ $0d4
AUD3PER     equ $0d6
AUD3VOL     equ $0d8
CIAAPRA     equ $bfe001

_LVOSupervisor    equ -30
_LVOForbid        equ -132
_LVOPermit        equ -138
_LVOOpenLibrary   equ -552
_LVOCloseLibrary  equ -414
_LVOLoadView      equ -222
_LVOWaitTOF       equ -270
_LVOOwnBlitter    equ -456
_LVODisownBlitter equ -462

sys_takeover:
    move.l  4.w,a6
    lea     gfxname(pc),a1
    moveq   #0,d0
    jsr     _LVOOpenLibrary(a6)
    move.l  d0,gfxbase
    beq.w   .fail
    move.l  d0,a6
    move.l  34(a6),oldview
    sub.l   a1,a1
    jsr     _LVOLoadView(a6)
    jsr     _LVOWaitTOF(a6)
    jsr     _LVOWaitTOF(a6)
    jsr     _LVOOwnBlitter(a6)

    move.l  4.w,a6
    moveq   #0,d0
    btst    #0,297(a6)
    beq.s   .vok
    lea     .get_vbr(pc),a5
    jsr     _LVOSupervisor(a6)
.vok:
    move.l  d0,vbr_base
    jsr     _LVOForbid(a6)

    lea     CUSTOM,a5
    move.w  INTENAR(a5),oldintena
    move.w  DMACONR(a5),olddmacon
    move.w  #$7fff,INTENA(a5)
    move.w  #$7fff,INTREQ(a5)
    move.w  #$7fff,DMACON(a5)

    move.l  #bpl1_a,disp_bpl1
    move.l  #bpl1_b,draw_bpl1
    move.l  #bpl2_a,disp_bpl2
    move.l  #bpl2_b,draw_bpl2
    move.l  #bpl3_a,disp_bpl3
    move.l  #bpl3_b,draw_bpl3
    move.w  #$8240,DMACON(a5)

    bsr.w   build_copper
    bsr.w   clear_draw_bpl
    lea     bpl3_a,a0
    bsr.w   blit_clear_full
    lea     bpl3_b,a0
    bsr.w   blit_clear_full
    bsr.w   swap_buffers
    bsr.w   clear_draw_bpl
    bsr.w   setup_paula

    move.l  vbr_base(pc),a0
    move.l  $6c(a0),old_vbl_vec
    move.l  #vbl_irq_handler,$6c(a0)

    move.l  #copperlist,COP1LC(a5)
    move.w  d0,COPJMP1(a5)
    move.w  #$83cf,DMACON(a5)
    move.w  #$c020,INTENA(a5)
    moveq   #1,d0
    rts
.fail:
    moveq   #0,d0
    rts
.get_vbr:
    movec   vbr,d0
    rte

sys_restore:
    lea     CUSTOM,a5
    bsr.w   wait_blitter
    move.w  #$7fff,INTENA(a5)
    move.w  #$7fff,INTREQ(a5)
    move.w  #$7fff,DMACON(a5)
    move.w  #0,AUD0VOL(a5)
    move.w  #0,AUD1VOL(a5)
    move.w  #0,AUD2VOL(a5)
    move.w  #0,AUD3VOL(a5)
    move.l  vbr_base(pc),a0
    move.l  old_vbl_vec(pc),$6c(a0)
    move.l  old_aud_vec(pc),$70(a0)
    move.w  #$0000,FMODE(a5)
    move.w  #$0c00,BPLCON3(a5)
    move.w  olddmacon(pc),d0
    or.w    #$8000,d0
    move.w  d0,DMACON(a5)
    move.w  oldintena(pc),d0
    or.w    #$8000,d0
    move.w  d0,INTENA(a5)
    move.l  gfxbase(pc),a6
    move.l  38(a6),COP1LC(a5)
    move.w  d0,COPJMP1(a5)
    jsr     _LVODisownBlitter(a6)
    move.l  oldview(pc),a1
    jsr     _LVOLoadView(a6)
    jsr     _LVOWaitTOF(a6)
    jsr     _LVOWaitTOF(a6)
    move.l  4.w,a6
    jsr     _LVOPermit(a6)
    move.l  gfxbase(pc),a1
    jsr     _LVOCloseLibrary(a6)
    rts

swap_buffers:
    move.l  disp_bpl1(pc),d0
    move.l  draw_bpl1(pc),d1
    move.l  d1,disp_bpl1
    move.l  d0,draw_bpl1
    move.l  d1,$0e0(a5)
    move.l  cop_bpl1_ptr(pc),a0
    move.w  d1,2(a0)
    swap    d1
    move.w  d1,6(a0)

    move.l  disp_bpl2(pc),d0
    move.l  draw_bpl2(pc),d1
    move.l  d1,disp_bpl2
    move.l  d0,draw_bpl2
    move.l  d1,$0e4(a5)
    move.l  cop_bpl2_ptr(pc),a0
    move.w  d1,2(a0)
    swap    d1
    move.w  d1,6(a0)

    move.l  disp_bpl3(pc),d0
    move.l  draw_bpl3(pc),d1
    move.l  d1,disp_bpl3
    move.l  d0,draw_bpl3
    move.l  d1,$0e8(a5)
    move.l  cop_bpl3_ptr(pc),a0
    move.w  d1,2(a0)
    swap    d1
    move.w  d1,6(a0)
    rts

wait_blitter:
    btst    #6,DMACONR(a5)
.wb: btst   #6,DMACONR(a5)
    bne.s   .wb
    rts

blit_clear_full:
    bsr.w   wait_blitter
    move.w  #$0100,BLTCON0(a5)
    move.w  #$0000,BLTCON1(a5)
    move.w  #0,BLTDMOD(a5)
    move.l  a0,BLTDPTH(a5)
    move.w  #$4014,BLTSIZE(a5)
    rts

clear_draw_bpl:
    move.l  draw_bpl1(pc),a0
    bsr.w   blit_clear_full
    move.l  draw_bpl2(pc),a0
    bsr.w   blit_clear_full
    bsr.w   wait_blitter
    rts

apply_blitter_aa:
    bsr.w   wait_blitter
    move.l  draw_bpl1(pc),a0
    move.l  a0,a1
    add.w   #40,a1
    move.l  draw_bpl3(pc),a2
    move.w  #$1dfc,BLTCON0(a5)
    move.w  #$0000,BLTCON1(a5)
    move.w  #$ffff,BLTAFWM(a5)
    move.w  #$ffff,BLTALWM(a5)
    move.w  #0,BLTAMOD(a5)
    move.w  #0,BLTBMOD(a5)
    move.w  #0,BLTDMOD(a5)
    move.l  a0,BLTAPTH(a5)
    move.l  a1,BLTBPTH(a5)
    move.l  a2,BLTDPTH(a5)
    move.w  #(255<<6)|20,BLTSIZE(a5)
    bsr.w   wait_blitter
    move.l  draw_bpl3(pc),a0
    add.l   #255*40,a0
    moveq   #9,d0
.clr_last:
    clr.l   (a0)+
    dbf     d0,.clr_last
    rts

wait_vbl:
    bsr.w   wait_blitter
    move.b  #1,swap_ready
.wv:
    tst.b   swap_ready
    bne.s   .wv
    rts

set_col01_shade:
    move.l  cop_pal_ptr(pc),a0
    move.w  d0,6(a0)
    move.w  d0,22(a0)
    and.w   #$000f,d0
    add.w   #$000e,d0
    lsr.w   #1,d0
    move.w  d0,d1
    lsl.w   #4,d1
    or.w    d0,d1
    lsl.w   #4,d1
    or.w    d0,d1
    move.w  d1,18(a0)
    rts

build_copper:
    lea     copperlist,a0
    move.l  #(FMODE<<16)|$0000,(a0)+
    move.l  #(DIWSTRT<<16)|$2c81,(a0)+
    move.l  #(DIWSTOP<<16)|$2cc1,(a0)+
    move.l  #(DDFSTRT<<16)|$0038,(a0)+
    move.l  #(DDFSTOP<<16)|$00d0,(a0)+
    move.l  #(BPLCON0<<16)|$3200,(a0)+
    move.l  #(BPLCON1<<16)|$0000,(a0)+
    move.l  #(BPLCON2<<16)|$0024,(a0)+
    move.l  #(BPL1MOD<<16)|$0000,(a0)+
    move.l  #(BPL2MOD<<16)|$0000,(a0)+

    move.l  a0,cop_bpl1_ptr
    move.l  disp_bpl1(pc),d0
    move.w  #$00e2,(a0)+
    move.w  d0,(a0)+
    swap    d0
    move.w  #$00e0,(a0)+
    move.w  d0,(a0)+

    move.l  a0,cop_bpl2_ptr
    move.l  disp_bpl2(pc),d0
    move.w  #$00e6,(a0)+
    move.w  d0,(a0)+
    swap    d0
    move.w  #$00e4,(a0)+
    move.w  d0,(a0)+

    move.l  a0,cop_bpl3_ptr
    move.l  disp_bpl3(pc),d0
    move.w  #$00ea,(a0)+
    move.w  d0,(a0)+
    swap    d0
    move.w  #$00e8,(a0)+
    move.w  d0,(a0)+

    move.l  #(BPLCON3<<16)|$0000,(a0)+
    move.l  a0,cop_pal_ptr
    move.l  #(COLOR00<<16)|$0eee,(a0)+
    move.l  #(COLOR01<<16)|$0111,(a0)+
    move.l  #(COLOR02<<16)|$0e11,(a0)+
    move.l  #(COLOR03<<16)|$0e11,(a0)+
    move.l  #(COLOR04<<16)|$0888,(a0)+
    move.l  #(COLOR05<<16)|$0111,(a0)+
    move.l  #(COLOR06<<16)|$0e11,(a0)+
    move.l  #(COLOR07<<16)|$0e11,(a0)+
    move.l  #$fffffffe,(a0)+
    rts
