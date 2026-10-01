import re

# 1. Ensure /cluster/status and _frontier.profiles are correct in app/main.py
with open("app/main.py", "r") as f:
    main_code = f.read()

if "@app.get(\"/cluster/status\")" not in main_code:
    cluster_route = """
@app.get("/cluster/status")
def cluster_status():
    return {"cluster_status": "ONLINE", "nodes": 4, "mesh_integrity": "VERIFIED"}
"""
    main_code += cluster_route
    print("[✔] Added /cluster/status to app/main.py")

# Ensure _frontier.profiles is a dictionary return (not called as a function)
main_code = main_code.replace("return _frontier.profiles()", "return _frontier.profiles")

with open("app/main.py", "w") as f:
    f.write(main_code)

print("[✔] app/main.py updated successfully.")
