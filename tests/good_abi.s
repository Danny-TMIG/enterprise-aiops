.global good_function
.text
good_function:
    // Proper 16-byte aligned stack allocation (32 bytes)
    sub sp, sp, #32
    
    // Save Frame Pointer (x29), Link Register (x30), and callee-saved x19
    stp x29, x30, [sp, #16]
    str x19, [sp, #8]
    
    // Valid nested call (LR is preserved)
    bl target_subroutine
    
    // Fully restore registers and stack before return
    ldr x19, [sp, #8]
    ldp x29, x30, [sp, #16]
    add sp, sp, #32
    ret
