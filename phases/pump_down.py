import numpy as np

from utils.recipe import P_VACUUM_HPA


def pump_down(measurements, bench, ui, log):
    """Pump-down to the ECSS pressure requirement; the time it takes is a
    health figure for the chamber and for the unit's outgassing load."""
    cap = bench.pump_down()
    ui.pump_progress = 100
    t = np.array(cap["time_h"]); p = np.array(cap["pressure_hpa"])
    below = np.flatnonzero(p <= P_VACUUM_HPA)
    t_vac = float(t[below[0]]) if below.size else float(t[-1])
    measurements.pumpdown.x_axis = cap["time_h"]
    measurements.pumpdown.y_axis.pressure = cap["pressure_hpa"]
    measurements.pumpdown.y_axis.pressure.aggregations.final_hpa = float(p[-1])
    measurements.pumpdown.y_axis.pressure.aggregations.time_to_vacuum_h = t_vac
    log.info(f"Pump-down: {p[-1]:.1e} hPa after {t[-1]:.1f} h, under {P_VACUUM_HPA:.0e} hPa at {t_vac:.2f} h")
