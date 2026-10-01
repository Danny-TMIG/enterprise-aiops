(module
  (memory (export "mem") 1)
  (func (export "validate_state_wasm") (param i32) (result i32)
    local.get 0
    i32.const 0
    i32.ne
  )
)
