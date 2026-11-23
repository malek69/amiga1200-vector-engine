; [EN/PL] MODULE: vec3d_engine.i | Fast-RAM XOR Scanline Polygon Rasterizer
init_fill_lut:
    movem.l d0-d6/a0,-(sp)
    lea     fill_lut,a0
    moveq   #0,d5
.cl: moveq  #0,d4
.wl: move.w d5,d2
    moveq   #0,d3
    moveq   #15,d1
.bl: btst   d1,d4
    sne     d0
    and.w   #1,d0
    eor.w   d0,d2
    or.w    d2,d0
    beq.s   .ns
    bset    d1,d3
.ns: dbf    d1,.bl
    moveq   #0,d0
    tst.w   d2
    beq.s   .nc
    move.l  #$00010000,d0
.nc: move.w d3,d0
    move.l  d0,(a0)+
    addq.w  #1,d4
    bne.s   .wl
    addq.w  #1,d5
    cmp.w   #2,d5
    blo.s   .cl
    movem.l (sp)+,d0-d6/a0
    rts

draw_polygon_mode:
    movem.l d0-d7/a0/a2-a5,-(sp)
    move.w  d0,-(sp)
    move.w  (a1)+,d7
    cmp.w   #3,d7
    blo.w   .pa
    move.w  #319,bbox_x1
    move.w  #0,bbox_x2
    move.w  #255,bbox_y1
    move.w  #0,bbox_y2
    move.w  (a1)+,d0
    move.w  (a1)+,d1
    move.w  d0,d4
    move.w  d1,d5
    subq.w  #2,d7
.el: move.w (a1)+,d2
    move.w  (a1)+,d3
    bsr.w   .ed
    move.w  d2,d0
    move.w  d3,d1
    dbf     d7,.el
    move.w  d4,d2
    move.w  d3,d1
    move.w  d5,d3
    bsr.w   .ed
    move.w  bbox_y1(pc),d2
    move.w  bbox_y2(pc),d3
    cmp.w   d2,d3
    blo.w   .pa
    move.w  bbox_x1(pc),d0
    lsr.w   #4,d0
    move.w  bbox_x2(pc),d1
    lsr.w   #4,d1
    move.w  d1,d4
    sub.w   d0,d4
    move.w  d3,d5
    sub.w   d2,d5
    move.w  d2,d6
    mulu.w  #40,d6
    move.w  d0,d7
    add.w   d7,d7
    add.w   d7,d6
    lea     edge_buf,a0
    add.l   d6,a0
    move.w  (sp)+,d0
    move.l  draw_bpl1(pc),a2
    cmp.w   #2,d0
    bne.s   .to
    move.l  draw_bpl2(pc),a2
.to: add.l  d6,a2
    moveq   #40,d7
    sub.w   d4,d7
    sub.w   d4,d7
    subq.w  #2,d7
    lea     fill_lut,a3
.yl: moveq  #0,d1
    move.w  d4,d6
.xl: moveq  #0,d2
    move.w  (a0),d2
    clr.w   (a0)+
    add.l   d1,d2
    move.l  (a3,d2.l*4),d3
    or.w    d3,(a2)+
    swap    d3
    move.l  d3,d1
    swap    d1
    dbf     d6,.xl
    add.w   d7,a0
    add.w   d7,a2
    dbf     d5,.yl
    movem.l (sp)+,d0-d7/a0/a2-a5
    rts
.pa: addq.l #2,sp
    movem.l (sp)+,d0-d7/a0/a2-a5
    rts
.ed: movem.l d0-d7/a0,-(sp)
    tst.w   d1
    bpl.s   .y0a
    moveq   #0,d1
.y0a: cmp.w #255,d1
    ble.s   .y0b
    move.w  #255,d1
.y0b: tst.w d3
    bpl.s   .y1a
    moveq   #0,d3
.y1a: cmp.w #255,d3
    ble.s   .y1b
    move.w  #255,d3
.y1b: cmp.w d1,d3
    beq.w   .ex
    bgt.s   .ys
    exg     d0,d2
    exg     d1,d3
.ys: cmp.w  bbox_y1(pc),d1
    bge.s   .ny1
    move.w  d1,bbox_y1
.ny1: move.w d3,d6
    subq.w  #1,d6
    cmp.w   bbox_y2(pc),d6
    ble.s   .ny2
    move.w  d6,bbox_y2
.ny2: move.w d0,d6
    move.w  d2,d7
    cmp.w   d6,d7
    bge.s   .xm
    exg     d6,d7
.xm: cmp.w  bbox_x1(pc),d6
    bge.s   .nx1
    move.w  d6,bbox_x1
.nx1: cmp.w bbox_x2(pc),d7
    ble.s   .nx2
    move.w  d7,bbox_x2
.nx2: move.w d3,d6
    sub.w   d1,d6
    ext.l   d6
    move.w  d2,d7
    sub.w   d0,d7
    ext.l   d7
    swap    d7
    divs.l  d6,d7
    swap    d0
    move.w  #$8000,d0
    lea     edge_buf,a0
    move.w  d1,d4
    mulu.w  #40,d4
    add.l   d4,a0
    subq.w  #1,d6
.sy: move.l d0,d4
    swap    d4
    tst.w   d4
    bpl.s   .sx0
    moveq   #0,d4
.sx0: cmp.w #319,d4
    ble.s   .sx1
    move.w  #319,d4
.sx1: move.w d4,d5
    lsr.w   #3,d5
    not.w   d4
    and.w   #7,d4
    bchg    d4,(a0,d5.w)
    add.l   d7,d0
    lea     40(a0),a0
    dbf     d6,.sy
.ex: movem.l (sp)+,d0-d7/a0
    rts
