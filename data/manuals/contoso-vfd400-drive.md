# Contoso VFD-400 Variable Frequency Drive: Service Manual

> Fictional sample manual for the Field Service Copilot demo. Not real equipment.

Document ID: MAN-VFD400 · Revision 6 · Drives 15 kW to 90 kW, 400 V class. Commonly used to control the CP-200 pump and the AC-75V compressor.

## 1. Safety

Dangerous voltage remains on the DC bus after the supply is switched off. After isolating and locking out the supply, **wait at least 15 minutes** and verify less than 50 V DC across terminals DC+ and DC- with a meter before touching anything inside the drive. The charge LED going out is not a safe indication on its own.

## 2. Fault codes

| Code | Name | Typical causes |
|---|---|---|
| F01 | Overcurrent | Acceleration time too short, motor cable short circuit, mechanical jam of the driven load |
| F02 | Overvoltage on DC bus | Deceleration too fast, high-inertia load feeding energy back, supply voltage spikes |
| F03 | Undervoltage | Supply dip, loose supply terminal, failed pre-charge circuit |
| F04 | Ground fault | Damaged motor cable insulation, moisture in the motor terminal box |
| F05 | Drive overtemperature | Cooling fan failed, blocked heatsink, cabinet too hot |
| F06 | Motor overload (I²t) | Motor running above rated current for too long |
| F07 | Communication loss | Fieldbus cable fault, controller stopped |

## 3. Troubleshooting

### 3.1 Drive trips on overcurrent (F01)

If F01 happens during start-up, increase the acceleration time (parameter P1.04, default 10 s) in steps of 5 s. If it happens during steady running, check the driven machine for a jam or a seized bearing; for example a CP-200 pump with failed bearings (BRG-6205-2RS) can draw high current. If it happens immediately on the run command, disconnect the motor cable and megger-test it at 1000 V: insulation must exceed 100 MΩ.

### 3.2 Drive trips on overvoltage when stopping (F02)

The load is regenerating energy into the drive faster than it can absorb. Increase the deceleration time (parameter P1.05, default 10 s), or enable the overvoltage controller (P2.11 = 1). For loads that must stop quickly, fit a braking resistor kit (part BRK-400-R).

### 3.3 Drive overheating (F05)

The drive derates above 40 °C ambient. Check the cooling fan (part FAN-400-12) spins freely and the heatsink fins are clean. A fan that does not start at power-up should be replaced; the fan has an expected life of about 40000 hours.

### 3.4 Motor runs but is noisy or vibrates at certain speeds

Mechanical resonance at specific speeds is common with pumps and fans. Use the skip-frequency parameters P3.01 to P3.04 to jump over the resonant band. Before blaming the drive, confirm the motor and pump coupling are aligned.

## 4. Procedures

### 4.1 Cooling fan replacement (FAN-400-12)

Estimated time: 30 minutes.

1. Isolate, lock out and wait 15 minutes. Verify the DC bus is below 50 V (section 1).
2. Remove the top cover (4 screws).
3. Unplug the fan connector and release the two clips.
4. Fit the new fan with the airflow arrow pointing **up**, away from the heatsink.
5. Refit the cover, power up and confirm the fan runs (parameter P0.15 shows fan speed).

### 4.2 Resetting a fault

Fix the cause first. Then press STOP/RESET on the keypad or send a reset over fieldbus. Faults F04 (ground fault) can only be reset after a power cycle, by design, so that a technician has to attend.

## 5. Key parameters

| Parameter | Name | Default |
|---|---|---|
| P1.04 | Acceleration time | 10 s |
| P1.05 | Deceleration time | 10 s |
| P2.11 | Overvoltage controller | 1 (on) |
| P3.01 to P3.04 | Skip frequency bands | 0 (off) |
| P0.15 | Cooling fan speed (read only) | n/a |

## 6. Spare parts

| Part number | Description |
|---|---|
| FAN-400-12 | Cooling fan assembly |
| BRK-400-R | Braking resistor kit |
| KPD-400 | Keypad with display |
| CAP-400-DC | DC bus capacitor bank (service centre only) |
