; ============================================================================
;  MODULE: whdload_slave.s | Custom Kickstart-Free WHDLoad Slave v17
;  INFO: Relocates Hunk segments (code, pcmdata, chipdata, fastram_bss)
;        directly into Fast/Chip RAM with ws_KickSize=0 (no Kickstart ROM).
; ============================================================================
    machine 68020
    section code,code
ws: moveq #-1,d0
    rts
    dc.b "WHDLOADS"
    dc.w 17,$0026
    dc.l $200000,0
    dc.w _start-ws,0,0
    dc.b 0,$59
    dc.l ${EXP_MEM}
    dc.w _n-ws,_c-ws,_i-ws,0
    dc.l 0
    dc.w 0,0
_n: dc.b "{DEMO_TITLE}",0
_c: dc.b "{DEMO_CREDITS}",0
_i: dc.b "AGA 320x256 Vector Engine + 16.5kHz Paula Audio",0
_e: dc.b "{EXE_NAME}",0
    even
rl: dc.l 0
hb: dcb.l 8,0
_start:
    lea rl(pc),a1
    move.l a0,(a1)
    move.l a0,a2
    lea $1000.w,a6
    move.l a6,4.w
    move.w #$0003,296(a6)
    move.w #$4ef9,-30(a6)
    lea s_sup(pc),a0
    move.l a0,-28(a6)
    move.w #$4ef9,-132(a6)
    lea s_rts(pc),a0
    move.l a0,-130(a6)
    move.w #$4ef9,-138(a6)
    move.l a0,-136(a6)
    move.w #$4ef9,-414(a6)
    move.l a0,-412(a6)
    move.w #$4ef9,-552(a6)
    lea s_opn(pc),a0
    move.l a0,-550(a6)
    lea $1400.w,a3
    lea s_cop(pc),a0
    move.l a0,38(a3)
    move.w #$4ef9,-222(a3)
    lea s_rts(pc),a0
    move.l a0,-220(a3)
    move.w #$4ef9,-456(a3)
    move.l a0,-454(a3)
    move.w #$4ef9,-462(a3)
    move.l a0,-460(a3)
    move.w #$4ef9,-270(a3)
    lea s_tof(pc),a0
    move.l a0,-268(a3)
    lea _e(pc),a0
    move.l ws+$20(pc),a1
    add.l #${LOAD_OFF},a1
    jsr 8(a2)
    move.l ws+$20(pc),a0
    add.l #${LOAD_OFF},a0
    cmp.l #$000003f3,(a0)+
    bne.w .ex
    addq.l #4,a0
    move.l (a0)+,d6
    addq.l #8,a0
    move.l #$00010000,d3
    move.l ws+$20(pc),d4
    lea hb(pc),a3
    move.w d6,d7
    subq.w #1,d7
.al: move.l (a0)+,d0
    move.l d0,d1
    and.l #$3fffffff,d1
    lsl.l #2,d1
    add.l #16,d1
    and.l #$fffffff0,d1
    btst #30,d0
    beq.s .fa
    move.l d3,(a3)+
    add.l d1,d3
    bra.s .an
.fa: move.l d4,(a3)+
    add.l d1,d4
.an: dbf d7,.al
    lea hb(pc),a3
    moveq #0,d5
.hl: cmp.w d6,d5
    bhs.s .rn
    move.l (a0)+,d0
    and.l #$0000ffff,d0
    cmp.w #$03e9,d0
    beq.s .cd
    cmp.w #$03ea,d0
    beq.s .cd
    cmp.w #$03eb,d0
    beq.s .db
    cmp.w #$03ec,d0
    beq.s .dr
    cmp.w #$03f2,d0
    bne.s .hl
    addq.w #1,d5
    bra.s .hl
.cd: move.l (a0)+,d1
    move.l (a3,d5.w*4),a1
    tst.l d1
    beq.s .hl
.cl: move.l (a0)+,(a1)+
    subq.l #1,d1
    bne.s .cl
    bra.s .hl
.db: move.l (a0)+,d1
    move.l (a3,d5.w*4),a1
    tst.l d1
    beq.s .hl
.zb: clr.l (a1)+
    subq.l #1,d1
    bne.s .zb
    bra.s .hl
.dr: move.l (a0)+,d1
    beq.s .hl
    move.l (a0)+,d2
    move.l (a3,d2.w*4),d2
    move.l (a3,d5.w*4),a1
.rl: move.l (a0)+,d4
    add.l d2,(a1,d4.l)
    subq.l #1,d1
    bne.s .rl
    bra.s .dr
.rn: movec cacr,d0
    or.w #$0808,d0
    movec d0,cacr
    move.l hb(pc),a0
    jsr (a0)
.ex: pea -1.w
    move.l rl(pc),a0
    jmp 4(a0)
s_opn: move.l #$1400,d0
s_rts: rts
s_sup: moveq #0,d0
    rts
s_tof: move.l $dff004,d0
    and.l #$1ff00,d0
    cmp.l #$12000,d0
    bne.s s_tof
    rts
s_cop: dc.l $01000200,$fffffffe
    end
