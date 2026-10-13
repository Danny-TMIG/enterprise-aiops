import subprocess, sys, os, time

def boot():
    print("[ASF-00] Booting Generative Self-Derived Fabric...")
    subprocess.run([sys.executable, "90_PROVENANCE_AND_SUPERSEDED_ARTIFACT_INDEX/generate_provenance_records.py"])
    
    processes = []
    try:
        processes.append(subprocess.Popen(["node", "20_GOVERNANCE/state/machine.js"], stdin=subprocess.PIPE, stdout=subprocess.PIPE))
        processes.append(subprocess.Popen([sys.executable, "-m", "uvicorn", "95_OPERATIONS.app.__main__:app", "--host", "127.0.0.1", "--port", "8000"]))
        
        time.sleep(2)
        subprocess.run([sys.executable, "99_COMMAND/tui/dashboard.py"])
        
        print("\n[ASF-00] Fabric fully operational. Press Ctrl+C to exit.\n")
        while True: time.sleep(1)
    except KeyboardInterrupt:
        for p in processes: p.terminate()
        print("\n[ASF-00] Fabric successfully halted.")

if __name__ == "__main__": boot()
