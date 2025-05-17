#!/usr/bin/env python3
"""
bme680_iaq_burnin_resume.py
===========================

Burn‑in‑/Kalibrier‑Skript für Bosch **BME680/BME688** mit BSEC 2.x (pi3g‑Bibliothek)
-----------------------------------------------------------------

⚡ **v1.4 (2025‑05‑11)** – Standardmäßig **silent** (kein „SET BME68X CONFIG“‑Spam)
und optional mit `--debug` wieder einschaltbar.

Änderungen v1.4
---------------
* **Debug‑Ausgaben** der pi3g‑Bibliothek werden jetzt nach dem Init mit
  `sensor.disable_debug_mode()` ausgeschaltet.  Per CLI‑Flag `--debug` kann
  man sie wieder aktivieren (dann ruft das Skript `enable_debug_mode()`).
* Kleinere kosmetische Fixes in den CLI‑Meldungen (UTF‑8).

---

```bash
sudo python3 bme680_iaq_burnin_resume.py --hours 24         # leise
sudo python3 bme680_iaq_burnin_resume.py --debug --hours 24 # detailiert
```
"""

from __future__ import annotations

import argparse, datetime, json, signal, sys, time
from pathlib import Path
from typing import Optional, Tuple

import smbus2
import bme68x
import bsecConstants as bsec

DEFAULT_STATE_PATH     = "bsec_iaq_state.json"
DEFAULT_PROGRESS_PATH  = "bsec_iaq_progress.json"
DEFAULT_BURNIN_HOURS   = 24
STATUS_PERIOD          = 60   # Sekunden zwischen Status‑Zeilen
EXPECTED_CHIP_IDS      = {0x61: "BME680", 0x62: "BME688"}

###############################################################################
# Hilfsfunktionen                                                            #
###############################################################################

def fmt(sec: float | int) -> str:
    """Format Sekunden ► HH:MM:SS"""
    return str(datetime.timedelta(seconds=int(sec)))

# ---------------------------------------------------------------------------
# Low‑Level I2C Utilities
# ---------------------------------------------------------------------------

def probe_chip_id(bus: int, addr: int) -> Optional[int]:
    """Liest CHIP_ID (Reg 0xD0); liefert None bei Fehler."""
    try:
        with smbus2.SMBus(bus) as sm:
            return sm.read_byte_data(addr, 0xD0)
    except OSError:
        return None

# ---------------------------------------------------------------------------
# Sensor‑Initialisierung
# ---------------------------------------------------------------------------

def init_sensor(bus: int, addr_pref: Optional[int], sample_rate: int, dbg: bool) -> Tuple[bme68x.BME68X, int]:
    """Initialisiert den Sensor; liefert (sensor, genutzte Adresse)."""
    candidates = [a for a in (addr_pref, 0x76, 0x77) if a is not None]
    last_exc: Optional[Exception] = None
    for addr in candidates:
        chip_id = probe_chip_id(bus, addr)
        if chip_id not in EXPECTED_CHIP_IDS:
            continue
        try:
            sensor = bme68x.BME68X(addr, 1)  # Legacy‑kompatibler Init
            if dbg:
                sensor.enable_debug_mode()
            else:
                sensor.disable_debug_mode()
            sensor.set_sample_rate(sample_rate)
            print(f"[I2C] {EXPECTED_CHIP_IDS[chip_id]} erkannt – Bus {bus}, Addr 0x{addr:02X}")
            return sensor, addr
        except Exception as e:
            last_exc = e
    print("\n[FEHLER] Kein ansprechbarer BME68x Sensor gefunden.")
    if last_exc:
        print(f"Letzte Fehlermeldung: {last_exc}")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Progress‑/State‑Dateien
# ---------------------------------------------------------------------------

def save_state(sensor: bme68x.BME68X, path: Path):
    path.write_text(json.dumps(sensor.get_bsec_state()))
    print(f"[BSEC] Finaler State → {path}")


def save_progress(sensor: bme68x.BME68X, elapsed: float, path: Path):
    path.write_text(json.dumps({"elapsed": elapsed, "state": sensor.get_bsec_state()}))


def load_progress(path: Path):
    try:
        data = json.loads(path.read_text())
        return float(data.get("elapsed", 0)), data.get("state")
    except Exception:
        return 0.0, None

###############################################################################
# Main                                                                        #
###############################################################################

def main() -> None:
    cli = argparse.ArgumentParser(description="Burn‑in / IAQ‑Kalibrierung für BME68x + BSEC")
    cli.add_argument("--bus", type=int, default=1, help="I²C‑Bus (Default 1)")
    cli.add_argument("--i2c", type=lambda x: int(x, 0), default=None, help="Bevorzugte I²C‑Adresse (0x76/0x77)")
    cli.add_argument("--hours", type=float, default=DEFAULT_BURNIN_HOURS, help="Zieldauer in Stunden")
    cli.add_argument("--state", default=DEFAULT_STATE_PATH, help="Pfad finaler BSEC‑State (JSON)")
    cli.add_argument("--progress", default=DEFAULT_PROGRESS_PATH, help="Pfad Resume‑Zwischenstand")
    cli.add_argument("--no-resume", action="store_true", help="Fortsetzung deaktivieren")
    cli.add_argument("--sample-rate", type=int, default=bsec.BSEC_SAMPLE_RATE_LP, help="BSEC Sampling‑Rate (1=ULP,2=LP,3=HP)")
    cli.add_argument("--debug", action="store_true", help="Verbose Sensor‑Debug ausgeben")
    args = cli.parse_args()

    state_p    = Path(args.state)
    prog_p     = Path(args.progress)

    sensor, addr = init_sensor(args.bus, args.i2c, args.sample_rate, args.debug)

    # Resume
    elapsed_prev = 0.0
    if not args.no_resume and prog_p.exists():
        elapsed_prev, s_state = load_progress(prog_p)
        if s_state:
            sensor.set_bsec_state(s_state)
            print(f"[RESUME] Fortsetzung nach {fmt(elapsed_prev)}")
    elif state_p.exists():
        try:
            sensor.set_bsec_state(json.loads(state_p.read_text()))
            print("[BSEC] Vorheriger End‑State geladen (schnellerer Anlauf).")
        except Exception:
            pass

    target_s = args.hours * 3600
    start_t  = time.time() - elapsed_prev
    last_stat = 0.0

    def on_exit(_sig=None, _frm=None):
        print("\n[EXIT] Speichere Zwischenstand …")
        save_progress(sensor, time.time() - start_t, prog_p)
        sensor.close_i2c()
        sys.exit(0)

    signal.signal(signal.SIGINT, on_exit)
    signal.signal(signal.SIGTERM, on_exit)

    print(f"[BURN‑IN] Ziel {fmt(target_s)} oder iaq_accuracy 3")
    print("Zeit      ⏱ elapsed  ⏳ remaining   IAQ  Acc")

    while True:
        try:
            raw = sensor.get_bsec_data()
        except Exception as e:
            print(f"\n[FEHLER] get_bsec_data(): {e}"); time.sleep(0.5); continue

        if not raw or raw == {}:
            time.sleep(0.1)
            continue

        if isinstance(raw, dict):
            iaq = raw.get("iaq"); acc = raw.get("iaq_accuracy")
        else:
            try:
                _, _, iaq, acc, *_ = raw
            except ValueError:
                time.sleep(0.1); continue

        now = time.time(); elapsed = now - start_t
        if now - last_stat >= STATUS_PERIOD:
            remaining = max(target_s - elapsed, 0)
            print(f"{time.strftime('%H:%M:%S')}  {fmt(elapsed):>8}  {fmt(remaining):>9}  {iaq:5.1f}   {acc}")
            save_progress(sensor, elapsed, prog_p)
            last_stat = now

        if acc == 3 or elapsed >= target_s:
            # Erfolgskriterium erreicht → letzte Werte ausgeben
            print(f"[BSEC] Burn‑in abgeschlossen bei {fmt(elapsed)} – IAQ {iaq:.1f}, Accuracy {acc}")
            break

        time.sleep(3 if args.sample_rate == bsec.BSEC_SAMPLE_RATE_LP else 1)

    save_state(sensor, state_p); prog_p.unlink(missing_ok=True); sensor.close_i2c(); print("[OK] Fertig. State gespeichert.")

###############################################################################

if __name__ == "__main__":
    main()
