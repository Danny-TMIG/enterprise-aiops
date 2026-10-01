.global bad_function
.text
bad_function:
    // Violation 1: Stack allocation is 24 bytes (not a multiple of 16)
    sub sp, sp, #24

    // Violation 2: Saves callee-saved registers x19/x20, but never restores them
    stp x19, x20, [sp, #8]

    // Violation 3: Non-leaf function branch-with-link (bl) without saving x30 (LR)
    bl target_subroutine

    add sp, sp, #24
    ret
