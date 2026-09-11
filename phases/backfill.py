def backfill(measurements, bench, log):
    """Teardown: the chamber is backfilled with dry nitrogen only once
    the unit is above the room's dew point; the optics must not fog."""
    r = bench.backfill()
    measurements.unit_temp_backfill_c = r["unit_temp_c"]
    measurements.pressure_end_hpa = r["pressure_hpa"]
    log.info(f"Backfill at {r['unit_temp_c']} C on the unit, chamber at {r['pressure_hpa']:.0f} hPa")
