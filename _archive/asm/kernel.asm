bits 64
global _acquire_lock_asm
section .text
_acquire_lock_asm:
    mov rax, 1
    lock xchg [rdi], rax
    test rax, rax
    jz .acquired
    mov rax, 0
    ret
.acquired:
    mov rax, 1
    ret
