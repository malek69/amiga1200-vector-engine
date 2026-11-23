CUSTOM      equ $dff000
DMACONR     equ $002
INTENA      equ $09a
INTREQR     equ $01e
INTREQ      equ $09c
DMACON      equ $096
BLTCON0     equ $040
BLTCON1     equ $042
BLTDPTH     equ $054
BLTSIZE     equ $058
BLTDMOD     equ $066
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

sys_takeover:
    movem.l d0-d7/a0-a6,-(sp)
    move.l  4.w,a6
    lea     .get_vbr(pc),a5
    jsr     -30(a6)
    move.l  d0,vbr_base
    jsr     -132(a6)
    lea     CUSTOM,a5
    move.w  #$7fff,DMACON(a5)
    move.w  #$7fff,INTENA(a5)
    move.w  #$7fff,INTREQ(a5)
    move.l  #bpl_buf_a,disp_bpl1
    move.l  #bpl_buf_a+10240,disp_bpl2
    move.l  #bpl_buf_b,draw_bpl1
    move.l  #bpl_buf_b+10240,draw_bpl2
    bsr.w   swap_buffers
    move.l  #copper_list,COP1LC(a5)
    move.w  d0,COPJMP1(a5)
    move.w  #$83cf,DMACON(a5)
    move.l  vbr_base(pc),a0
    move.l  #vbl_irq_handler,$6c(a0)
    move.w  #$c020,INTENA(a5)
    movem.l (sp)+,d0-d7/a0-a6
    moveq   #1,d0
    rts
.get_vbr:
    movec   vbr,d0
    rte

sys_restore:
    lea     CUSTOM,a5
    move.w  #$7fff,INTENA(a5)
    move.w  #$7fff,DMACON(a5)
    move.l  4.w,a6
    jsr     -138(a6)
    rts

wait_vbl:
    bsr.w   wait_blitter
    move.b  #1,swap_ready
.wv: tst.b  swap_ready
    bne.s   .wv
    rts

swap_buffers:
    lea     copper_list,a0
    move.l  disp_bpl1(pc),d0
    move.l  draw_bpl1(pc),d1
    move.l  d1,disp_bpl1
    move.l  d0,draw_bpl1
    move.w  d1,46(a0)
    swap    d1
    move.w  d1,42(a0)
    move.l  disp_bpl2(pc),d0
    move.l  draw_bpl2(pc),d1
    move.l  d1,disp_bpl2
    move.l  d0,draw_bpl2
    move.w  d1,54(a0)
    swap    d1
    move.w  d1,50(a0)
    rts

wait_blitter:
    lea     CUSTOM,a5
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

vbl_irq_handler:
    movem.l d0-d1/a0/a5,-(sp)
    lea     CUSTOM,a5
    move.w  INTREQR(a5),d0
    btst    #5,d0
    beq.s   .vexit
    addq.l  #1,vbl_tick
    tst.b   swap_ready
    beq.s   .vack
    bsr.w   swap_buffers
    clr.b   swap_ready
.vack:
    move.w  #$0020,INTREQ(a5)
.vexit:
    movem.l (sp)+,d0-d1/a0/a5
    rte

    even
vbl_tick:   dc.l 0
vbr_base:   dc.l 0
swap_ready: dc.b 0,0

    section cop_chip,data_c
    even
copper_list:
    dc.w    $0106,$0c00
    dc.w    $01fc,$0000
    dc.w    $008e,$2c81
    dc.w    $0090,$2cc1
    dc.w    $0092,$0038
    dc.w    $0094,$00d0
    dc.w    $0108,$0000
    dc.w    $010a,$0000
    dc.w    $0102,$0000
    dc.w    $0104,$0000
    dc.w    $00e0,$0000
    dc.w    $00e2,$0000
    dc.w    $00e4,$0000
    dc.w    $00e6,$0000
    dc.w    $0100,$2200
    dc.w    $ffff,$fffe
    section bpl_chip,bss_c
bpl_buf_a:  ds.b 20480
bpl_buf_b:  ds.b 20480
    section code,code
