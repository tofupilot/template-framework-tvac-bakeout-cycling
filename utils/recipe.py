"""Thermal vacuum recipe for a smallsat star tracker: bakeout with a
TQCM witness, then acceptance thermal vacuum cycling with a functional
check at every dwell, in one chamber run.

Where the numbers come from. ECSS-E-ST-10-03C Rev.1 thermal vacuum for
units: pressure at or below 1e-5 hPa, 4 acceptance cycles (8 for
qualification), a functional test at the hot and cold dwells, the
acceptance levels the operating range plus margin. The bakeout has no
standard duration: it ends when the outgassing rate seen by a
thermoelectric quartz crystal microbalance (TQCM) at its collection
temperature falls under the programme's rate for long enough. On this
programme the crystal at -20 C must read under 1 Hz/h for the last
6 h of a bake of at least 36 h at +60 C; the total frequency shift
over the bake is the mass the witness collected. Optics are why: a
star tracker's lens and baffle collect what the harness and the
potting outgas, and the functional check at each dwell is a centroid
error against a simulated star through the chamber window."""

P_VACUUM_HPA = 1e-5
PUMPDOWN_MAX_H = 8.0

BAKEOUT_T_C = 60.0
BAKEOUT_MIN_H = 36.0
BAKEOUT_MAX_H = 72.0
TQCM_T_C = -20.0
TQCM_RATE_HZ_PER_H_MAX = 1.0
TQCM_CLEAN_WINDOW_H = 6.0
TQCM_TOTAL_SHIFT_HZ_MAX = 800.0   # mass collected over the bake, programme limit for optics

T_OP_MIN_C = -25.0
T_OP_MAX_C = 50.0
MARGIN_C = 5.0
T_ACC_MIN_C = T_OP_MIN_C - MARGIN_C
T_ACC_MAX_C = T_OP_MAX_C + MARGIN_C
CYCLES = 4
DWELL_MIN = 120.0
CENTROID_ERR_ARCSEC_MAX = 10.0    # functional check at each dwell, simulated star through the window
POWER_W_MAX = 3.5

BACKFILL_T_MIN_C = 15.0           # unit above the room's dew point before dry nitrogen comes in
TIME_SCALE = 0.0                  # mock returns the pump-down, the bake and the cycles in one call each
