import numpy as np

from utils.recipe import CYCLES, T_ACC_MAX_C, T_ACC_MIN_C


def tvac_cycling(measurements, bench, ui, log):
    """ECSS acceptance thermal vacuum cycling: four cycles between the
    acceptance levels, the tracker powered, a functional check at every
    dwell: centroid of a simulated star through the window, bus power."""
    cap = bench.thermal_cycles()
    ui.cycle_progress = 100
    u = np.array(cap["unit_c"])
    hot = sum(1 for d in cap["dwell_temp_c"] if d >= T_ACC_MAX_C - 1.0)
    cold = sum(1 for d in cap["dwell_temp_c"] if d <= T_ACC_MIN_C + 1.0)
    cycles = int(min(hot, cold))

    measurements.profile.x_axis = [round(m / 60.0, 2) for m in cap["time_min"]]
    measurements.profile.y_axis.unit = cap["unit_c"]
    measurements.profile.y_axis.unit.aggregations.cycles = cycles
    measurements.profile.y_axis.unit.aggregations.min_c = float(u.min())
    measurements.profile.y_axis.unit.aggregations.max_c = float(u.max())

    measurements.dwells.x_axis = list(range(1, len(cap["dwell_temp_c"]) + 1))
    measurements.dwells.y_axis.temperature = cap["dwell_temp_c"]
    measurements.dwells.y_axis.centroid = cap["dwell_centroid_arcsec"]
    measurements.dwells.y_axis.centroid.aggregations.max_arcsec = float(max(cap["dwell_centroid_arcsec"]))
    measurements.dwells.y_axis.power = cap["dwell_power_w"]
    measurements.dwells.y_axis.power.aggregations.max_w = float(max(cap["dwell_power_w"]))
    log.info(f"{cycles}/{CYCLES} cycles, unit {u.min():.1f}..{u.max():.1f} C, centroid error up to {max(cap['dwell_centroid_arcsec']):.1f} arcsec, power up to {max(cap['dwell_power_w']):.2f} W at the dwells")
