AUDIO_BUF_SIZE equ 2048
setup_paula:
    bset    #1,$bfe001
    lea     CUSTOM,a5
    move.l  #pcm_start,pcm_pos
    move.l  #0,pcm_played
    move.l  #dma_buf_a,pcm_cur_buf
    move.l  #dma_buf_b,pcm_nxt_buf
    move.l  pcm_cur_buf(pc),a1
    bsr.w   fill_pcm_chunk
    move.l  pcm_nxt_buf(pc),a1
    bsr.w   fill_pcm_chunk
    move.l  vbr_base(pc),a0
    move.l  $70(a0),old_aud_vec
    move.l  #aud0_irq_handler,$70(a0)
    move.l  pcm_cur_buf(pc),d0
    move.l  d0,AUD0LCH(a5)
    move.l  d0,AUD1LCH(a5)
    move.l  d0,AUD2LCH(a5)
    move.l  d0,AUD3LCH(a5)
    move.w  #AUDIO_BUF_SIZE/2,AUD0LEN(a5)
    move.w  #AUDIO_BUF_SIZE/2,AUD1LEN(a5)
    move.w  #AUDIO_BUF_SIZE/2,AUD2LEN(a5)
    move.w  #AUDIO_BUF_SIZE/2,AUD3LEN(a5)
    move.w  #215,AUD0PER(a5)
    move.w  #215,AUD1PER(a5)
    move.w  #215,AUD2PER(a5)
    move.w  #215,AUD3PER(a5)
    move.w  #215,AUD0VOL(a5)
    move.w  #215,AUD1VOL(a5)
    move.w  #215,AUD2VOL(a5)
    move.w  #215,AUD3VOL(a5)
    move.w  #$0080,INTREQ(a5)
    move.w  #$820f,DMACON(a5)
    move.w  #$c080,INTENA(a5)
    rts
fill_pcm_chunk:
    move.l  pcm_pos(pc),a0
    lea     pcm_end,a2
    move.w  #AUDIO_BUF_SIZE-1,d0
.cp:
    cmp.l   a2,a0
    blo.s   .ok
    lea     pcm_start,a0
.ok:
    move.b  (a0)+,(a1)+
    dbf     d0,.cp
    move.l  a0,pcm_pos
    rts
aud0_irq_handler:
    movem.l d0-d2/a0-a2/a5,-(sp)
    lea     CUSTOM,a5
    move.w  INTREQR(a5),d0
    btst    #7,d0
    beq.s   .aexit
    move.w  #$0080,INTREQ(a5)
    move.l  pcm_played(pc),d0
    add.l   #AUDIO_BUF_SIZE,d0
    move.l  #pcm_end-pcm_start,d1
    cmp.l   d1,d0
    blo.s   .p_ok
    sub.l   d1,d0
.p_ok:
    move.l  d0,pcm_played
    move.l  pcm_cur_buf(pc),d0
    move.l  pcm_nxt_buf(pc),d1
    move.l  d1,pcm_cur_buf
    move.l  d0,pcm_nxt_buf
    move.l  d1,AUD0LCH(a5)
    move.l  d1,AUD1LCH(a5)
    move.l  d1,AUD2LCH(a5)
    move.l  d1,AUD3LCH(a5)
    move.l  d0,a1
    bsr.w   fill_pcm_chunk
.aexit:
    movem.l (sp)+,d0-d2/a0-a2/a5
    rte
