play_vector_frame:
    movem.l d0-d5/a0-a2,-(sp)
    moveq   #0,d0
    move.w  cur_frame(pc),d0
    lea     vec_frame_table,a0
    move.l  (a0,d0.l*4),a0
    lea     CUSTOM,a1
    move.w  #$0c00,BPLCON3(a1)
    addq.l  #2,a0
    move.w  #$0eee,COLOR00(a1)
    move.w  #$0111,COLOR01(a1)
    move.w  #$0e11,COLOR02(a1)
    move.w  #$0e11,COLOR03(a1)
.poly_loop:
    move.w  (a0)+,d0
    bmi.s   .frame_done
    move.l  a0,a1
    bsr.w   draw_polygon_mode
    moveq   #0,d1
    move.w  (a0)+,d1
    lsl.l   #2,d1
    add.l   d1,a0
    bra.s   .poly_loop
.frame_done:
    movem.l (sp)+,d0-d5/a0-a2
    rts
