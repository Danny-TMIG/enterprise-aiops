from app.seed.manifest import Manifest, CPVORates, load_manifest


# ── self-registration as capability `seed` ───────────────────────
def _self_register():
    try:
        from app.core.capabilities import register
    except Exception:
        return

    @register("seed")
    def _entry(*args, **kwargs):
        return {"module": "app.seed", "code": "seed", "package": True}


_self_register()
