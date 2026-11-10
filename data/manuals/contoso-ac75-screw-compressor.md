# Contoso AC-75 Rotary Screw Air Compressor: Service Manual

> Fictional sample manual for the Field Service Copilot demo. Not real equipment.

Document ID: MAN-AC75 · Revision 2 · Oil-injected, air-cooled models AC-75 and AC-75V (variable speed).

## 1. Safety

Never service the compressor while it is pressurised. Stop the unit, apply lockout/tagout (LOTO), and wait until the separator tank gauge reads 0 bar before loosening any fitting or filter. Compressor oil can exceed 90 °C; let the unit cool for 15 minutes. Compressed air must never be pointed at skin.

## 2. Specifications

| Item | Value |
|---|---|
| Free air delivery | 12.5 m³/min at 7.5 bar |
| Maximum working pressure | 10 bar |
| Motor | 75 kW |
| Oil capacity | 38 L, synthetic compressor oil part OIL-SYN-46-20L |
| Normal discharge temperature | 75 to 95 °C |
| Cooling | Air-cooled, combined oil/air cooler |

## 3. Alarm and warning codes

| Code | Meaning | First check |
|---|---|---|
| A201 | High discharge temperature (above 105 °C, unit trips) | Blocked cooler, low oil level, high room temperature |
| A202 | Low oil pressure | Oil level, oil filter OF-75-10 clogged |
| A203 | Separator differential pressure high (above 1 bar) | Separator element SEP-75-30 saturated |
| A204 | Air filter restricted | Air filter AF-75-20 dirty |
| A205 | Motor overload | Supply voltage, belt tension (AC-75 only), bearing wear |
| W210 | Service due | Service counter reached 4000 h |

## 4. Troubleshooting

### 4.1 Compressor overheating or tripping on temperature (alarm A201)

The most common causes, in order:

1. **Dirty cooler fins.** Dust and oil mist clog the cooler. Clean with low-pressure air from the fan side outward, or with a degreaser. A clogged cooler is the cause in more than half of A201 trips.
2. **Low oil level.** Check the sight glass with the unit stopped. Top up with OIL-SYN-46-20L only. Mixing oil types can cause foaming.
3. **Poor room ventilation.** Ambient temperature must stay below 40 °C. Hot exhaust air must not recirculate to the intake.
4. **Thermostatic valve stuck.** If the cooler stays cold while the oil is hot, the thermostatic valve (part TV-75-70) is stuck closed.

### 4.2 Oil in the compressed air (oil carry-over)

Oil droplets at the outlet or oily water at drains point to a saturated or damaged separator element (SEP-75-30), a blocked scavenge line orifice, or an overfilled oil tank. Check alarm A203 history.

### 4.3 Knocking, rattling or unusual noise

A knocking sound at startup often means a loose coupling element or worn motor bearings. A high-pitched whine that changes with load usually indicates airend bearing wear; airend bearings are not field-serviceable and require an airend exchange (part AE-75-EXCH).

### 4.4 Compressor does not reach set pressure

Check for air leaks in the plant network first (a leak test at weekends is the cheapest win). Then check the inlet valve opens fully and the air filter (AF-75-20) is not restricted (A204).

## 5. Procedures

### 5.1 Oil and filter change

Estimated time: 1.5 hours.

1. Run the unit for 5 minutes so the oil is warm and drains fully, then stop, apply LOTO and depressurise.
2. Drain the oil from the separator tank drain valve.
3. Replace the oil filter OF-75-10: lubricate the new gasket with oil and hand-tighten plus three quarters of a turn.
4. Refill with 38 L of OIL-SYN-46-20L.
5. Run for 10 minutes, check for leaks, recheck oil level.

### 5.2 Separator element replacement (SEP-75-30)

Replace every 4000 h or when the separator differential pressure exceeds 1 bar (A203). Earthing the element is mandatory: the element has a staple in its gasket that must stay in place to prevent static discharge.

## 6. Maintenance schedule

| Interval | Task |
|---|---|
| Daily | Check oil level and drain condensate |
| Every 2000 h | Clean cooler, replace air filter AF-75-20 |
| Every 4000 h | Oil change, oil filter OF-75-10, separator SEP-75-30 |
| Every 24000 h | Motor bearings, thermostatic valve TV-75-70 |

## 7. Spare parts

| Part number | Description |
|---|---|
| OF-75-10 | Oil filter |
| AF-75-20 | Air intake filter element |
| SEP-75-30 | Oil separator element |
| TV-75-70 | Thermostatic valve kit |
| OIL-SYN-46-20L | Synthetic compressor oil, 20 L |
| AE-75-EXCH | Airend exchange unit |
