BPL_SIZE equ 40*256
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
    bsr.w   wait_vbl
    move.l  draw_bpl1(pc),a0
    bsr.w   blit_clear_full
    bsr.w   wait_blitter
    move.l  draw_bpl2(pc),a0
    bsr.w   blit_clear_full
    bsr.w   wait_blitter
    move.l  vbl_tick(pc),d0
    move.w  vec_frame_count(pc),d1
    cmp.w   d1,d0
    blo.s   .f_ok
    moveq   #0,d0
    move.l  #0,vbl_tick
.f_ok:
    move.w  d0,cur_frame
    bsr.w   play_vector_frame
    move.b  #1,swap_ready
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
    even
pcm_pos:     dc.l 0
pcm_played:  dc.l 0
pcm_cur_buf: dc.l 0
pcm_nxt_buf: dc.l 0
old_aud_vec: dc.l 0
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
    section code,code
    even
disp_bpl1:  dc.l 0
disp_bpl2:  dc.l 0
disp_bpl3:  dc.l 0
disp_bpl4:  dc.l 0
disp_bpl5:  dc.l 0
disp_bpl6:  dc.l 0
disp_bpl7:  dc.l 0
disp_bpl8:  dc.l 0
draw_bpl1:  dc.l 0
draw_bpl2:  dc.l 0
draw_bpl3:  dc.l 0
draw_bpl4:  dc.l 0
draw_bpl5:  dc.l 0
draw_bpl6:  dc.l 0
draw_bpl7:  dc.l 0
draw_bpl8:  dc.l 0
    section vec_fast,bss_p
edge_buf: ds.b 40*256
    section code,code
    even
cur_frame:  dc.w 0
bbox_x1:    dc.w 0
bbox_x2:    dc.w 0
bbox_y1:    dc.w 0
bbox_y2:    dc.w 0
    section vec_fast,bss_p
fill_lut:   ds.l 131072
