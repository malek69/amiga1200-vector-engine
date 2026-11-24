BPL_SIZE equ 80*256
    machine 68020
    section code,code
start:
    movem.l d0-a6,-(sp)
    bsr.w   sys_takeover
    tst.l   d0
    beq.w   exit_program
    bsr.w   init_fill_lut
    bsr.w   setup_paula
    move.l  #0,vbl_tick
mainloop:
    bsr.w   clear_fast_buffers
    move.l  vbl_tick(pc),d0
    move.w  vec_frame_count(pc),d1
    cmp.w   d1,d0
    blo.s   .f_ok
    moveq   #0,d0
    move.l  #0,vbl_tick
.f_ok:
    move.w  d0,cur_frame
    bsr.w   play_vector_frame
    bsr.w   copy_fast_to_chip
    bsr.w   wait_vbl
    btst    #6,CIAAPRA
    beq.s   shutdown

    cmp.b   #$75,$bfec01
    bne.w   mainloop
shutdown:
    bsr.w   sys_restore
exit_program:
    movem.l (sp)+,d0-a6
    moveq   #0,d0
    rts

clear_fast_buffers:
    movem.l d0-d7/a0-a4,-(sp)
    lea     fast_bpl1+40960,a0
    moveq   #0,d0
    moveq   #0,d1
    moveq   #0,d2
    moveq   #0,d3
    moveq   #0,d4
    moveq   #0,d5
    moveq   #0,d6
    moveq   #0,d7
    sub.l   a1,a1
    sub.l   a2,a2
    sub.l   a3,a3
    sub.l   a4,a4
    move.w  #853-1,d7
.cl_lp:
    movem.l d0-d6/a1-a4,-(a0)
    move.l  d0,-(a0)
    dbf     d7,.cl_lp
    movem.l d0-d3,-(a0)
    movem.l (sp)+,d0-d7/a0-a4
    rts

copy_fast_to_chip:
    movem.l d0-d7/a0-a5,-(sp)
    lea     fast_bpl1,a0
    move.l  draw_bpl1(pc),a1
    bsr.s   .copy_plane
    lea     fast_bpl2,a0
    move.l  draw_bpl2(pc),a1
    bsr.s   .copy_plane
    movem.l (sp)+,d0-d7/a0-a5
    rts
.copy_plane:
    move.w  #426-1,d7
.cp_lp:
    movem.l (a0)+,d0-d6/a2-a5
    movem.l d0-d6/a2-a5,(a1)
    move.l  (a0)+,44(a1)
    lea     48(a1),a1
    dbf     d7,.cp_lp
    movem.l (a0)+,d0-d6/a2
    movem.l d0-d6/a2,(a1)
    rts

    even
pcm_pos:     dc.l 0
pcm_played:  dc.l 0
pcm_cur_buf: dc.l 0
pcm_nxt_buf: dc.l 0
old_aud_vec: dc.l 0
disp_bpl1:   dc.l 0
disp_bpl2:   dc.l 0
draw_bpl1:   dc.l 0
draw_bpl2:   dc.l 0
cur_frame:   dc.w 0
bbox_x1:     dc.w 0
bbox_x2:     dc.w 0
bbox_y1:     dc.w 0
bbox_y2:     dc.w 0
    include "gfx_engine.i"
    include "vec3d_engine.i"
    include "scene_player.i"
    include "audio_player.i"
    include "scene_data.i"
    section audio_fast,data_p
pcm_start:
    incbin  "median_audio.raw"
pcm_end:
    section audio_chip,bss_c
dma_buf_a: ds.b 2048
dma_buf_b: ds.b 2048
    section vec_fast,bss_p
fill_lut:  ds.l 131072
edge_buf:  ds.b 80*256
fast_bpl1: ds.b 80*256
fast_bpl2: ds.b 80*256
