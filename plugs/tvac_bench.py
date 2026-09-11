"""Thermal vacuum bench (mock): a chamber with a shroud and a heater
plate, a turbo pump with an ion gauge, a TQCM on a cold finger facing
the unit, and the star tracker's telemetry and image link.

Maps to a chamber controller over Modbus (shroud, plate, valves), an
ion gauge over RS-232, a QCM controller of the CrystalTek or QCM
Research class over its serial protocol, and the tracker's link over
Ethernet for power, temperature and the centroid of a simulated star
projected through the window. The mock synthesizes a healthy unit:
pump-down to 5e-6 hPa in five hours, an outgassing rate that decays
from 40 Hz/h with an 8 h time constant, four clean cycles with a
centroid error that grows a few arcseconds at the cold end. Swap for
classes speaking the chamber's and the tracker's protocols; the phases
stay unchanged.
"""

import numpy as np

from utils.recipe import BAKEOUT_MIN_H, BAKEOUT_T_C, CYCLES, DWELL_MIN, T_ACC_MAX_C, T_ACC_MIN_C, TQCM_T_C


class TvacBench:
    def __init__(self):
        self._rng = np.random.default_rng(1005)
        self._pressure_hpa = 1013.0
        self._unit_c = 22.0
        self._tqcm_hz = 0.0
        # self.chamber = modbus...; self.gauge = serial...; self.qcm = ...; self.tracker = socket...
        print("TVAC bench ready, chamber at ambient, door closed")

    def identify(self):
        return {"firmware": "3.1.0", "unit_temp_c": round(self._unit_c, 1), "pressure_hpa": round(self._pressure_hpa, 1)}

    def pump_down(self):
        """Roughing then turbo, ion gauge logged every 5 min until the
        pressure is under the requirement and stable."""
        t = np.arange(0.0, 5.5, 5.0 / 60.0)
        p = 1013.0 * np.exp(-t * 4.2) + 5e-6 * (1.0 + 0.3 * np.exp(-t / 2.0))
        p *= 1.0 + self._rng.normal(0.0, 0.02, t.size)
        self._pressure_hpa = float(p[-1])
        return {"time_h": t.round(3).tolist(), "pressure_hpa": [float(f"{x:.3g}") for x in p]}

    def bakeout(self, max_h):
        """Plate at +60 C, TQCM crystal at -20 C facing the unit, crystal
        frequency logged every 15 min. Ends when the programme's rate
        criterion holds or at max_h."""
        t = np.arange(0.0, max_h + 0.25, 0.25)
        rate = 40.0 * np.exp(-t / 8.0) + 0.15
        freq = np.cumsum(rate) * 0.25
        freq += self._rng.normal(0.0, 0.3, t.size)
        unit = 22.0 + (BAKEOUT_T_C - 22.0) * (1.0 - np.exp(-t / 1.5)) + self._rng.normal(0.0, 0.1, t.size)
        # The bench stops the bake once the rate has been clean for the window past the minimum.
        clean = np.flatnonzero((rate < 1.0) & (t >= BAKEOUT_MIN_H))
        end = int(clean[0] + 8.0 / 0.25) + 1 if clean.size else t.size
        end = min(end, t.size)
        self._tqcm_hz = float(freq[end - 1])
        self._unit_c = 22.0  # plate off, unit back to ambient before the cycles
        return {"time_h": t[:end].round(2).tolist(), "tqcm_hz": freq[:end].round(1).tolist(), "unit_c": unit[:end].round(2).tolist()}

    def thermal_cycles(self):
        """Four cycles between the acceptance levels through the shroud
        and the plate, unit temperature logged every minute; the tracker
        powered and its centroid read at each dwell."""
        t, unit, dwell_t, dwell_err, dwell_p = [], [], [], [], []
        minute = 0
        cur = self._unit_c
        rate = 1.5  # C/min under vacuum, radiative plus the plate

        def go(to):
            nonlocal minute, cur
            while abs(to - cur) > rate:
                cur += rate * np.sign(to - cur)
                t.append(minute); unit.append(round(cur + self._rng.normal(0.0, 0.08), 2)); minute += 1
            cur = to

        def dwell():
            nonlocal minute
            for _ in range(int(DWELL_MIN)):
                t.append(minute); unit.append(round(cur + self._rng.normal(0.0, 0.08), 2)); minute += 1
            dwell_t.append(cur)
            err = 3.2 + 0.055 * max(0.0, 20.0 - cur) + 0.02 * max(0.0, cur - 40.0) + self._rng.normal(0.0, 0.2)
            dwell_err.append(round(err, 2))
            dwell_p.append(round(2.6 + 0.004 * max(0.0, cur - 20.0) + self._rng.normal(0.0, 0.02), 3))

        for _ in range(CYCLES):
            go(T_ACC_MAX_C); dwell()
            go(T_ACC_MIN_C); dwell()
        go(22.0)
        self._unit_c = 22.0
        return {"time_min": t, "unit_c": unit, "dwell_temp_c": dwell_t, "dwell_centroid_arcsec": dwell_err, "dwell_power_w": dwell_p}

    def backfill(self):
        """Dry nitrogen to ambient once the unit is above the dew point."""
        self._pressure_hpa = 1012.0
        return {"unit_temp_c": round(self._unit_c, 1), "pressure_hpa": self._pressure_hpa}

    def __del__(self):
        print("Chamber at ambient, shroud off")
