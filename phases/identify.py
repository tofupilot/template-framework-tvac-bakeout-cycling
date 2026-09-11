def identify(measurements, bench, unit, log):
    """Setup: tracker telemetry, firmware, chamber at ambient with the
    door closed, TQCM zeroed on the record."""
    ident = bench.identify()
    measurements.firmware_version = ident["firmware"]
    measurements.unit_temp_start_c = ident["unit_temp_c"]
    measurements.pressure_start_hpa = ident["pressure_hpa"]
    unit.metadata["chamber_id"] = "TVAC-1"
    log.info(f"Star tracker {unit.serial_number}: fw {ident['firmware']}, {ident['unit_temp_c']} C, chamber at {ident['pressure_hpa']:.0f} hPa")
