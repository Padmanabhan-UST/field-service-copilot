# Contoso CP-200 Centrifugal Pump: Service Manual

> Fictional sample manual for the Field Service Copilot demo. Not real equipment.

Document ID: MAN-CP200 · Revision 4 · Applies to serial numbers CP200-1000 and later.

## 1. Safety

Always apply lockout/tagout (LOTO) to the motor starter before opening the pump casing or touching the coupling. Close the suction and discharge isolation valves and drain the casing. The casing can stay hot (above 60 °C) for up to 30 minutes after shutdown. Wear cut-resistant gloves when handling the impeller; vane edges are sharp.

## 2. Specifications

| Item | Value |
|---|---|
| Rated flow | 200 m³/h |
| Rated head | 45 m |
| Speed | 2950 rpm (50 Hz) |
| Motor | 37 kW, 400 V, 3-phase |
| Bearings | Drive end and non-drive end: deep groove ball bearing, part BRG-6205-2RS |
| Mechanical seal | Single cartridge seal, part SEAL-MS-35 |
| Impeller | Closed, 5 vanes, part IMP-CP200-5V |
| Lubrication | Grease, lithium complex NLGI 2, part GRS-LC2-400G |

## 3. Vibration limits

Vibration is measured as velocity RMS on the bearing housings, in mm/s.

| Zone | Velocity (mm/s) | Action |
|---|---|---|
| A: new machine | below 2.8 | None |
| B: acceptable | 2.8 to 4.5 | Normal operation |
| C: warning | 4.5 to 7.1 | Plan maintenance within 2 weeks |
| D: alarm | above 7.1 | Stop the pump and investigate (alarm E101) |

## 4. Alarm codes

| Code | Meaning | First check |
|---|---|---|
| E101 | High vibration (above 7.1 mm/s) | Coupling alignment, bearing condition, cavitation |
| E102 | High bearing temperature (above 85 °C) | Grease quantity and condition, bearing wear |
| E103 | Low suction pressure | Suction strainer blocked, suction valve partly closed |
| E104 | Seal leak detected | Mechanical seal SEAL-MS-35 worn or dry-run damage |
| E105 | Motor overload trip | Pump running far right of curve, impeller rubbing |

## 5. Troubleshooting

### 5.1 Excessive vibration or noise (alarm E101)

Work through the causes in this order, from most to least common:

1. **Shaft misalignment.** Check coupling alignment with a laser tool. Tolerance: 0.05 mm offset, 0.05 mm/100 mm angularity. Misalignment usually shows as high vibration at 2× running speed.
2. **Worn bearings.** A grinding or rumbling sound from the bearing housing, often with rising temperature (E102). Replace both bearings as a set (BRG-6205-2RS, see section 6.1).
3. **Cavitation.** A crackling noise, like gravel passing through the pump, usually with low suction pressure (E103). Clean the suction strainer and fully open the suction valve. Do not throttle the suction side.
4. **Impeller imbalance or damage.** Debris lodged in the impeller or eroded vanes. Inspect and replace the impeller (IMP-CP200-5V) if vanes are eroded more than 2 mm.
5. **Loose base bolts.** Check foundation bolt torque: 120 N·m.

### 5.2 Pump runs but delivers low flow

Check for a closed or partly closed discharge valve, air in the suction line, a worn impeller, or a blocked suction strainer. Confirm the motor rotation direction; reversed rotation gives roughly 40% of rated flow.

### 5.3 Leak at the shaft seal (alarm E104)

A few drops per hour are normal while a new seal beds in during the first 24 hours. A steady stream means the seal faces are damaged; the most common cause is the pump running dry. Replace the cartridge seal SEAL-MS-35.

## 6. Procedures

### 6.1 Bearing replacement (BRG-6205-2RS)

Estimated time: 3 hours, two technicians.

1. Apply LOTO and drain the pump (section 1).
2. Remove the coupling guard and the coupling spacer.
3. Remove the bearing housing end covers.
4. Pull both bearings with a puller. Never reuse a bearing that has been pulled.
5. Heat new bearings to 100 °C with an induction heater and slide them onto the shaft. Do not hammer.
6. Pack each bearing one third full with grease GRS-LC2-400G.
7. Refit covers, re-align the coupling (tolerances in 5.1) and run for 30 minutes. Vibration must be in zone A or B.

### 6.2 Mechanical seal replacement (SEAL-MS-35)

Estimated time: 2 hours. The cartridge design means the seal is pre-set at the factory. Remove the old cartridge, clean the shaft sleeve, slide the new cartridge on, tighten set screws to 8 N·m and remove the setting clips **before** starting the pump. Starting with setting clips fitted destroys the seal.

## 7. Maintenance schedule

| Interval | Task |
|---|---|
| Daily | Check for leaks and unusual noise |
| Weekly | Record vibration and bearing temperature |
| Every 2000 h | Regrease bearings: 10 g per bearing of GRS-LC2-400G |
| Every 8000 h | Check alignment, inspect impeller |
| Every 16000 h | Replace bearings BRG-6205-2RS |

## 8. Spare parts

| Part number | Description | Recommended stock |
|---|---|---|
| BRG-6205-2RS | Deep groove ball bearing | 2 |
| SEAL-MS-35 | Cartridge mechanical seal, 35 mm | 1 |
| IMP-CP200-5V | Impeller, closed, 5 vanes | 1 |
| GSK-CP200-CAS | Casing gasket | 2 |
| GRS-LC2-400G | Bearing grease cartridge, 400 g | 2 |
