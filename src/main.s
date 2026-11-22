; ============================================================================
;  MODULE: main.s | Main Entry & Locked 50.00 Hz PAL Loop (Motorola 68020+)
;  FRAME PIPELINE:
;    1. start -> sys_takeover (take over AGA, Copper, Blitter, Paula & IRQs)
;    2. init_fill_lut (one-time 512 KB XOR prefix LUT generation in Fast RAM)
;    3. mainloop (50 Hz VBL):
;       - wait_vbl: sync to raster line Y=260 & swap double-buffers
;       - blit_clear_full: asynchronous Blitter clear of BPL2 (red plane)
;       - play_vector_frame: decode frame stream & rasterize into fast_bpl1
;       - .cp_fast / .clr_fast: 32-bit Fast-RAM -> Chip-RAM copy & clear
;       - apply_blitter_aa: hardware 1px Blitter anti-aliasing into BPL3
; ============================================================================

BPL_SIZE equ 40*256
    machine 68020
    section code,code

start:
    movem.l d0-a6,-(sp)
    bsr.w   init_fill_lut
    bsr.w   sys_takeover
    tst.l   d0
    beq.w   exit_program

    move.l  #0,vbl_tick

mainloop:
    bsr.w   wait_vbl
    move.l  draw_bpl2(pc),a0
    bsr.w   blit_clear_full

    ; Synchronizacja klatki z audio 16497 Hz: frame = (pcm_played * 10) / 5499
    move.l  vbl_tick(pc),d0
    ; 50Hz
    ; 50Hz
    move.w  vec_frame_count(pc),d1
    cmp.w   d1,d0
    blo.s   .f_ok
    moveq   #0,d0
.f_ok:
    move.w  d0,cur_frame

    bsr.w   wait_blitter
    bsr.w   play_vector_frame
    lea     fast_bpl1,a0
    move.l  draw_bpl1(pc),a1
    move.w  #639,d0
.cp_fast:
    move.l  (a0)+,(a1)+
    move.l  (a0)+,(a1)+
    move.l  (a0)+,(a1)+
    move.l  (a0)+,(a1)+
    dbf     d0,.cp_fast
    lea     fast_bpl1,a0
    moveq   #0,d1
    move.w  #639,d0
.clr_fast:
    move.l  d1,(a0)+
    move.l  d1,(a0)+
    move.l  d1,(a0)+
    move.l  d1,(a0)+
    dbf     d0,.clr_fast
    bsr.w   apply_blitter_aa

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

    include "gfx_engine.i"
    include "audio_player.i"
    include "vec3d_engine.i"
    include "scene_player.i"
    include "scene_data.i"

gfxname:        dc.b "graphics.library",0
                even
gfxbase:        dc.l 0
oldview:        dc.l 0
old_vbl_vec:    dc.l 0
old_aud_vec:    dc.l 0
vbr_base:       dc.l 0
disp_bpl1:      dc.l 0
disp_bpl2:      dc.l 0
disp_bpl3:      dc.l 0
draw_bpl1:      dc.l 0
draw_bpl2:      dc.l 0
draw_bpl3:      dc.l 0
cop_bpl1_ptr:   dc.l 0
cop_bpl2_ptr:   dc.l 0
cop_bpl3_ptr:   dc.l 0
cop_pal_ptr:    dc.l 0
oldintena:      dc.w 0
olddmacon:      dc.w 0
vbl_tick:       dc.l 0
cur_frame:      dc.w 0
bbox_x1:        dc.w 0
bbox_x2:        dc.w 0
bbox_y1:        dc.w 0
bbox_y2:        dc.w 0
swap_ready:     dc.b 0
                even
pcm_pos:        dc.l pcm_start
pcm_played:     dc.l 0
pcm_cur_buf:    dc.l dma_buf_a
pcm_nxt_buf:    dc.l dma_buf_b

inv_tab:
    dc.l $00000000,$00400000,$00200000,$00155555,$00100000,$000ccccc,$000aaaaa,$00092492
    dc.l $00080000,$00071c71,$00066666,$0005d174,$00055555,$0004ec4e,$00049249,$00044444
    dc.l $00040000,$0003c3c3,$00038e38,$00035e50,$00033333,$00030c30,$0002e8ba,$0002c859
    dc.l $0002aaaa,$00028f5c,$00027627,$00025ed0,$00024924,$000234f7,$00022222,$00021084
    dc.l $00020000,$0001f07c,$0001e1e1,$0001d41d,$0001c71c,$0001bacf,$0001af28,$0001a41a
    dc.l $00019999,$00018f9c,$00018618,$00017d05,$0001745d,$00016c16,$0001642c,$00015c98
    dc.l $00015555,$00014e5e,$000147ae,$00014141,$00013b13,$00013521,$00012f68,$000129e4
    dc.l $00012492,$00011f70,$00011a7b,$000115b1,$00011111,$00010c97,$00010842,$00010410
    dc.l $00010000,$0000fc0f,$0000f83e,$0000f489,$0000f0f0,$0000ed73,$0000ea0e,$0000e6c2
    dc.l $0000e38e,$0000e070,$0000dd67,$0000da74,$0000d794,$0000d4c7,$0000d20d,$0000cf64
    dc.l $0000cccc,$0000ca45,$0000c7ce,$0000c565,$0000c30c,$0000c0c0,$0000be82,$0000bc52
    dc.l $0000ba2e,$0000b817,$0000b60b,$0000b40b,$0000b216,$0000b02c,$0000ae4c,$0000ac76
    dc.l $0000aaaa,$0000a8e8,$0000a72f,$0000a57e,$0000a3d7,$0000a237,$0000a0a0,$00009f11
    dc.l $00009d89,$00009c09,$00009a90,$0000991f,$000097b4,$0000964f,$000094f2,$0000939a
    dc.l $00009249,$000090fd,$00008fb8,$00008e78,$00008d3d,$00008c08,$00008ad8,$000089ae
    dc.l $00008888,$00008767,$0000864b,$00008534,$00008421,$00008312,$00008208,$00008102
    dc.l $00008000,$00007f01,$00007e07,$00007d11,$00007c1f,$00007b30,$00007a44,$0000795c
    dc.l $00007878,$00007797,$000076b9,$000075de,$00007507,$00007432,$00007361,$00007292
    dc.l $000071c7,$000070fe,$00007038,$00006f74,$00006eb3,$00006df5,$00006d3a,$00006c80
    dc.l $00006bca,$00006b15,$00006a63,$000069b4,$00006906,$0000685b,$000067b2,$0000670b
    dc.l $00006666,$000065c3,$00006522,$00006483,$000063e7,$0000634c,$000062b2,$0000621b
    dc.l $00006186,$000060f2,$00006060,$00005fd0,$00005f41,$00005eb4,$00005e29,$00005d9f
    dc.l $00005d17,$00005c90,$00005c0b,$00005b87,$00005b05,$00005a84,$00005a05,$00005987
    dc.l $0000590b,$0000588f,$00005816,$0000579d,$00005726,$000056b0,$0000563b,$000055c7
    dc.l $00005555,$000054e4,$00005474,$00005405,$00005397,$0000532a,$000052bf,$00005254
    dc.l $000051eb,$00005183,$0000511b,$000050b5,$00005050,$00004fec,$00004f88,$00004f26
    dc.l $00004ec4,$00004e64,$00004e04,$00004da6,$00004d48,$00004ceb,$00004c8f,$00004c34
    dc.l $00004bda,$00004b80,$00004b27,$00004ad0,$00004a79,$00004a22,$000049cd,$00004978
    dc.l $00004924,$000048d1,$0000487e,$0000482d,$000047dc,$0000478b,$0000473c,$000046ed
    dc.l $0000469e,$00004651,$00004604,$000045b8,$0000456c,$00004521,$000044d7,$0000448d
    dc.l $00004444,$000043fb,$000043b3,$0000436c,$00004325,$000042df,$0000429a,$00004254
    dc.l $00004210,$000041cc,$00004189,$00004146,$00004104,$000040c2,$00004081,$00004040

    section pcmdata,data
pcm_start:
    incbin  "median_audio.raw"
pcm_end:
    dcb.b   256,0
    even

    section chipdata,bss_c
dma_buf_a:   ds.b 2048
dma_buf_b:   ds.b 2048
bpl1_a:      ds.b BPL_SIZE
bpl1_b:      ds.b BPL_SIZE
bpl2_a:      ds.b BPL_SIZE
bpl2_b:      ds.b BPL_SIZE
bpl3_a:      ds.b BPL_SIZE
bpl3_b:      ds.b BPL_SIZE
copperlist:  ds.b 512



    even

    section fastram_bss,bss
    even
fast_bpl1:
    ds.b    BPL_SIZE
edge_buf:
    ds.b    10240
fill_lut:
    ds.l    131072
    end
