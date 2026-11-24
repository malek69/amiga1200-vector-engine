import os, shutil, subprocess
def apply_profile(sd, profile, hz_target=12105):
    if profile == "standard": return hz_target, 312, 248, 4, 4, 550, ""
    h = 512 if profile == "060" else 256
    vh = 496 if profile == "060" else 248
    bpl_sz = 80 * h
    g = open(f"{sd}/gfx_engine.i").read()
    g = g.replace("move.l  #bpl_buf_a+10240,disp_bpl2", f"move.l  #bpl_buf_a+{bpl_sz},disp_bpl2")
    g = g.replace("move.l  #bpl_buf_b+10240,draw_bpl2", f"move.l  #bpl_buf_b+{bpl_sz},draw_bpl2")
    g = g.replace("dc.w    $0094,$00d0", "dc.w    $0094,$00d4")
    g = g.replace("dc.w    $0100,$2200", "dc.w    $0100,$a204" if profile == "060" else "dc.w    $0100,$a200")
    if profile == "060":
        g = g.replace("dc.w    $0108,$0000\n    dc.w    $010a,$0000", "dc.w    $0108,$0050\n    dc.w    $010a,$0050")
        g = g.replace("move.l  disp_bpl1(pc),d0", "move.l  disp_bpl1(pc),d0\n    btst    #7,$dff004\n    beq.s   .evf\n    add.l   #80,d0\n.evf:")
    g = g.replace("bpl_buf_a:  ds.b 20480\nbpl_buf_b:  ds.b 20480", f"bpl_buf_a:  ds.b {bpl_sz*2}\nbpl_buf_b:  ds.b {bpl_sz*2}")
    open(f"{sd}/gfx_engine.i", "w").write(g)
    ms = open(f"{sd}/main.s").read()
    ms = ms.replace("BPL_SIZE equ 40*256", f"BPL_SIZE equ 80*{h}")
    old_c = "    move.l  draw_bpl1(pc),a0\n    bsr.w   blit_clear_full\n    bsr.w   wait_blitter\n    move.l  draw_bpl2(pc),a0\n    bsr.w   blit_clear_full\n    bsr.w   wait_blitter"
    ms = ms.replace(old_c, "    bsr.w   clear_fast_buffers")
    ms = ms.replace("    bsr.w   play_vector_frame\n    bsr.w   wait_vbl", "    bsr.w   play_vector_frame\n    bsr.w   copy_fast_to_chip\n    bsr.w   wait_vbl")
    iters_cl = (bpl_sz * 2) // 48
    rem_cl = (bpl_sz * 2) % 48
    iters_cp = bpl_sz // 48
    rem_cp = bpl_sz % 48
    rt = f"""clear_fast_buffers:\n    movem.l d0-d7/a0-a4,-(sp)\n    lea     fast_bpl1+{bpl_sz*2},a0\n    moveq   #0,d0\n    moveq   #0,d1\n    moveq   #0,d2\n    moveq   #0,d3\n    moveq   #0,d4\n    moveq   #0,d5\n    moveq   #0,d6\n    moveq   #0,d7\n    sub.l   a1,a1\n    sub.l   a2,a2\n    sub.l   a3,a3\n    sub.l   a4,a4\n    move.w  #{iters_cl}-1,d7\n.cl_lp:\n    movem.l d0-d6/a1-a4,-(a0)\n    move.l  d0,-(a0)\n    dbf     d7,.cl_lp\n    {"movem.l d0-d3,-(a0)" if rem_cl==16 else "movem.l d0-d7,-(a0)"}\n    movem.l (sp)+,d0-d7/a0-a4\n    rts\ncopy_fast_to_chip:\n    movem.l d0-d7/a0-a5,-(sp)\n    lea     fast_bpl1,a0\n    move.l  draw_bpl1(pc),a1\n    bsr.s   .cp\n    lea     fast_bpl2,a0\n    move.l  draw_bpl2(pc),a1\n    bsr.s   .cp\n    movem.l (sp)+,d0-d7/a0-a5\n    rts\n.cp:\n    move.w  #{iters_cp}-1,d7\n.cpl:\n    movem.l (a0)+,d0-d6/a2-a5\n    movem.l d0-d6/a2-a5,(a1)\n    move.l  (a0)+,44(a1)\n    lea     48(a1),a1\n    dbf     d7,.cpl\n    {"movem.l (a0)+,d0-d6/a2\n    movem.l d0-d6/a2,(a1)" if rem_cp==32 else "movem.l (a0)+,d0-d3\n    movem.l d0-d3,(a1)"}\n    rts\n"""
    ms = ms.replace("exit_program:\n    movem.l (sp)+,d0-a6\n    moveq   #0,d0\n    rts", "exit_program:\n    movem.l (sp)+,d0-a6\n    moveq   #0,d0\n    rts\n" + rt)
    ms = ms.replace("edge_buf:  ds.b 40*256", f"edge_buf:  ds.b {bpl_sz}\nfast_bpl1: ds.b {bpl_sz}\nfast_bpl2: ds.b {bpl_sz}")
    open(f"{sd}/main.s", "w").write(ms)
    v3 = open(f"{sd}/vec3d_engine.i").read()
    v3 = v3.replace("move.w  #319,bbox_x1", "move.w  #639,bbox_x1").replace("cmp.w   #19,d1", "cmp.w   #39,d1")
    v3 = v3.replace("move.w  #255,bbox_y1", f"move.w  #{h-1},bbox_y1").replace("cmp.w  #255,d1", f"cmp.w  #{h-1},d1")
    v3 = v3.replace("mulu.w  #40,d6", "mulu.w  #80,d6").replace("mulu.w  #40,d4", "mulu.w  #80,d4")
    v3 = v3.replace("move.l  draw_bpl1(pc),a2", "lea     fast_bpl1,a2").replace("move.l  draw_bpl2(pc),a2", "lea     fast_bpl2,a2")
    v3 = v3.replace("moveq   #40,d7", "moveq   #80,d7").replace("cmp.w #318,d4", "cmp.w #638,d4").replace("move.w  #318,d4", "move.w  #638,d4")
    open(f"{sd}/vec3d_engine.i", "w").write(v3)
    if profile == "060":
        sl = open(f"{sd}/whdload_slave.s").read().replace("or.w #$0808,d0", "or.w #$0909,d0").replace("dc.l $00680000", "dc.l $00c00000")
        open(f"{sd}/whdload_slave.s", "w").write(sl)
    return (16497 if profile == "060" else 12105), 624, vh, 8, (8 if profile == "060" else 4), (1200 if profile == "060" else 650), ("_060_HiRes512" if profile == "060" else "_HiRes640")
