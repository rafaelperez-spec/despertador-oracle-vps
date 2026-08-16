import json
import urllib.request
import urllib.error
import time
import os
import sys

HISTORY_FILE = "history.json"

def record_history(run_record):
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []
            
    history.insert(0, run_record)
    history = history[:100]  # Guarda hasta 100 ejecuciones históricas
    
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[!] Error al actualizar history.json: {e}")

def main():
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    print("=" * 60)
    print("ANGELUS DESPERTADOR UNIFICADO - ORACLE CLOUD VPS")
    print(f"Fecha/Hora: {timestamp}")
    print("=" * 60)

    try:
        with open("services.json", "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception as e:
        print(f"[X] Error al cargar services.json: {e}")
        sys.exit(1)

    nodes = config.get("oracle_vps", [])
    print(f"[+] Evaluando {len(nodes)} nodos VPS en Oracle Cloud...\n")

    run_results = []

    for node in nodes:
        name = node.get("name", "Desconocido")
        url = node.get("url")
        channel = "Tailscale Mesh" if "100.125.56" in url else "IP Publica Oracle"
        node_result = {
            "node_name": name,
            "url": url,
            "channel": channel,
            "health_status": "FAILED",
            "health_code": 0,
            "radiomics_status": "N/A"
        }
        
        print(f"[*] Pinging {name} ({url})...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Angelus-KeepAlive/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                status = resp.getcode()
                body = resp.read().decode("utf-8")
                print(f"   [OK] Respuesta HTTP {status}")
                node_result["health_status"] = f"HTTP {status} OK"
                node_result["health_code"] = status
        except urllib.error.HTTPError as e:
            print(f"   [!] HTTP Error {e.code}: {e.reason}")
            node_result["health_status"] = f"HTTP Error {e.code}"
        except Exception as e:
            print(f"   [!] Error al conectar: {e}")
            node_result["health_status"] = f"Error: Timeout/Unreachable"

        # Prueba radiómica
        rad_url = node.get("radiomics_url")
        if rad_url:
            print(f"   [Test] Ejecutando Benchmark Radiomico en {name} ({rad_url})...")
            try:
                req = urllib.request.Request(rad_url, headers={"User-Agent": "Angelus-Radiomics/1.0"})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    print(f"   [OK] Benchmark Radiomico completado: {resp.read().decode('utf-8')[:120]}...")
                    node_result["radiomics_status"] = "GLCM Haralick Computed"
            except Exception as e:
                print(f"   [!] Error en prueba radiomica: {e}")
                node_result["radiomics_status"] = "Radiomics Error"

        run_results.append(node_result)
        print("-" * 50)

    # Registrar en history.json
    record_history({
        "timestamp": timestamp,
        "results": run_results
    })

    print("\n[+] Proceso de activacion y prueba finalizado exitosamente. Historial registrado.")

if __name__ == "__main__":
    main()
