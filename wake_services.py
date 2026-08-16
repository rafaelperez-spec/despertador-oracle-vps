import json
import urllib.request
import urllib.error
import time
import sys

def main():
    print("=" * 60)
    print("⏰ ANGELUS DESPERTADOR UNIFICADO - ORACLE CLOUD VPS")
    print(f"Fecha/Hora: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    print("=" * 60)

    try:
        with open("services.json", "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Error al cargar services.json: {e}")
        sys.exit(1)

    nodes = config.get("oracle_vps", [])
    print(f"📋 Evaluando {len(nodes)} nodos VPS en Oracle Cloud...\n")

    for node in nodes:
        name = node.get("name", "Desconocido")
        url = node.get("url")
        print(f"🔍 Pinging {name} ({url})...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Angelus-KeepAlive/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                status = resp.getcode()
                body = resp.read().decode("utf-8")
                print(f"   ✅ Respuesta HTTP {status} — OK")
                if "status" in body:
                    print(f"   📊 Health Data: {body[:120]}...")
        except urllib.error.HTTPError as e:
            print(f"   ⚠️ HTTP Error {e.code}: {e.reason}")
        except Exception as e:
            print(f"   ❌ Error al conectar: {e}")

        # Si el nodo tiene prueba radiómica en vivo
        rad_url = node.get("radiomics_url")
        if rad_url:
            print(f"   🧪 Ejecutando Benchmark Radiómico en {name} ({rad_url})...")
            try:
                req = urllib.request.Request(rad_url, headers={"User-Agent": "Angelus-Radiomics/1.0"})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    print(f"   ✅ Benchmark Radiómico completado: {resp.read().decode('utf-8')[:120]}...")
            except Exception as e:
                print(f"   ⚠️ Error en prueba radiómica: {e}")

        print("-" * 50)

    print("\n🎉 Proceso de activación y prueba finalizado exitosamente.")

if __name__ == "__main__":
    main()
