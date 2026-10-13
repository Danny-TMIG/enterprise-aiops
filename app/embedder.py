from mlx_lm import load

MODEL_ID = "mlx-community/Qwen2.5-7B-Instruct-4bit"
print(f"[-] Loading model weights & embedding matrices for [{MODEL_ID}]...")

model, tokenizer, _ = load(MODEL_ID)  # type: ignore[misc]

# Accessing the underlying token embedding weights matrix in MLX
# In MLX transformer models, token embeddings reside in model.model.embed_tokens
if hasattr(model, "model") and hasattr(model.model, "embed_tokens"):
    embed_weights = model.model.embed_tokens.weight
elif hasattr(model, "embed_tokens"):
    embed_weights = model.embed_tokens.weight
else:
    # Fallback search through parameters
    embed_weights = next(iter(model.parameters()))

print(f"[+] Embedding Matrix Shape: {embed_weights.shape}")
print(f"[+] Embedding Data Type: {embed_weights.dtype}")
print(f"[+] Total Embedding Parameters: {embed_weights.size:,}")

# Perform a live embedding lookup for sample text tokens
sample_text = "Sovereign M4 Max pipeline"
token_ids = tokenizer.encode(sample_text)
print(f"[-] Token IDs for lookup: {token_ids}")

# Slice embeddings for the tokens
if hasattr(embed_weights, "__getitem__"):
    sample_embeddings = embed_weights[token_ids]
    print(f"[+] Resulting Tensor Embedding Shape for tokens: {sample_embeddings.shape}")
