import numpy as np

from utils.recipe import BAKEOUT_MAX_H, BAKEOUT_T_C, TQCM_CLEAN_WINDOW_H, TQCM_RATE_HZ_PER_H_MAX


def bakeout(measurements, bench, ui, log):
    """Bake at +60 C with the TQCM at -20 C facing the unit. The crystal
    frequency is the mass collected; its slope is the outgassing rate.
    The bake is judged on how long the rate has been under the
    programme's figure at the end, and on the total mass collected."""
    cap = bench.bakeout(BAKEOUT_MAX_H)
    ui.bake_progress = 100
    t = np.array(cap["time_h"]); f = np.array(cap["tqcm_hz"])
    # Rate over a 2 h window, Hz/h, from the frequency curve.
    w = 8
    rate = np.full(t.size, np.nan)
    rate[w:] = (f[w:] - f[:-w]) / (t[w:] - t[:-w])
    rate_curve = np.where(np.isnan(rate), rate[w], rate)
    clean = rate_curve <= TQCM_RATE_HZ_PER_H_MAX
    # Clean window at the end: hours since the rate last exceeded the figure.
    dirty = np.flatnonzero(~clean)
    clean_h = float(t[-1] - t[dirty[-1]]) if dirty.size else float(t[-1])

    measurements.bake.x_axis = cap["time_h"]
    measurements.bake.y_axis.tqcm = cap["tqcm_hz"]
    measurements.bake.y_axis.tqcm.aggregations.duration_h = float(t[-1])
    measurements.bake.y_axis.tqcm.aggregations.total_shift_hz = float(f[-1] - f[0])
    measurements.bake.y_axis.rate = rate_curve.round(3).tolist()
    measurements.bake.y_axis.rate.aggregations.final_hz_per_h = float(rate_curve[-1])
    measurements.bake.y_axis.rate.aggregations.clean_window_h = clean_h
    measurements.bake.y_axis.unit = cap["unit_c"]
    measurements.bake.y_axis.unit.aggregations.max_c = float(max(cap["unit_c"]))
    log.info(f"Bake {t[-1]:.1f} h at {BAKEOUT_T_C:.0f} C: TQCM {f[-1] - f[0]:.0f} Hz collected, rate {rate_curve[-1]:.2f} Hz/h at the end, clean for the last {clean_h:.1f} h (needs {TQCM_CLEAN_WINDOW_H:.0f})")
