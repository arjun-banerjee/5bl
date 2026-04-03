# Lab Notebook Lab 10 
Arjun, Ines

71.4ohms - inductor resistance

## 1A
1.	Grabbed 10 kΩ resistor from kit — measured with DMM: 9.97 kΩ  ✓ (within 1%)
2.	47 μF capacitor — DMM reads: 48.2 μF  (within 5% tolerance, good)
3.	Built series RC on breadboard. R on top rail, C to ground. Connected CH1 across gen output, CH2 across cap.
4.	Function gen: square wave, 100 mHz, 10 Vpp, +5V DC offset → signal goes 0 V to 10 V
5.	Oscilloscope: ROLL mode, 400 ms/div, 2 V/div on CH2
τ_theory = RC = (10,000 Ω)(47 × 10⁻⁶ F) = 470 ms    period/2 = 10 s ≈ 5τ  ✓ (enough time to fully discharge)
Uncertainty: σ_τ/τ = √(0.01² + 0.05²) ≈ 0.051  →  σ_τ ≈ 24 ms  →  τ = 470 ± 24 ms
Froze scope at a clean discharge edge. Cursor A at t=0 (V=10.00 V), stepped cursor B to 9 successive points.
Cursor uncertainties: ±0.1 V (voltage), ±20 ms (time)  — set by display resolution at these gain settings
Sanity check: at t = τ ≈ 470 ms, V should be 10/e ≈ 3.68 V. Interpolating between t=400 (4.41V) and t=600 (2.86V): at 470 ms → ~3.8 V  ✓ roughly right
Will fit to V_C/V₀ = A·exp(–t/τ) using scipy.optimize.curve_fit in Python (done on laptop after lab).
–	Semi-log plot → straight line means single exponential ✓
–	Last two points (1800, 2400 ms) are at noise floor — will likely exclude
–	Expect A ≈ 1.0 (good voltage reference), τ_fit ≈ 470–490 ms

## 1B
–	Cut two pieces of Al foil to fit US Letter paper (215.9 mm × 279.4 mm)
–	Glued foil to opposite sides of paper with glue stick — paper = dielectric (ε_r ≈ 3.8, d ≈ 0.1 mm)
–	Attached jumper wires with alligator clips to each foil plate
A = 0.2159 × 0.2794 = 6.03 × 10⁻² m²,  d = 1 × 10⁻⁴ m,  ε_r = 3.8
C_theory = ε_r ε₀ A / d = (3.8)(8.854×10⁻¹²)(6.03×10⁻²) / (1×10⁻⁴) ≈ 20 nF
Tried to measure capacitance directly with DMM (200 nF range)... reads 0 nF  ??
Tested DMM with the 47 μF cap → reads correctly. So DMM is fine.
Decided to roll our flat cap into a cylinder to (a) measure geometry more precisely and (b) see if DMM could pick it up better.
Measured with ruler:
–	Inner radius a = 1.5 cm  (around the cardboard tube we used as a core)
–	Outer radius b = 2.7 cm
–	Length L = 22.4 cm
Cylindrical capacitor formula: C = 2π ε_r ε₀ L / ln(b/a)
= 2π (3.8)(8.854×10⁻¹²)(0.224) / ln(0.027/0.014)
= 2π (3.8)(8.854×10⁻¹²)(0.224) / ln(1.929)
ln(1.929) ≈ 0.657
= (4.751×10⁻¹¹) / 0.657 ≈ 72 nF  (cylindrical estimate)
Substituted homemade cap into Exp 1A circuit. Changed gen to 1 Hz square wave to look for a slower response.
Oscilloscope showed essentially a square wave on CH2 — no rounding at all.
Switched to 1 MΩ resistor. Still square-ish but very slight rounding visible.
Effective d from back-calc: d_eff = ε_r ε₀ A / C = (3.8)(8.85e-12)(6.03e-2) / 1.6e-9 ≈ 1.27 mm  — 12× thicker than paper alone → glue is dominating the dielectric separation
This makes sense — the glue layer adds a lot to effective d. Plus glue might be slightly conductive (parallel resistance path), further reducing apparent C on DMM.

## 2A
L = 100 mH inductor. Measured R_L with DMM: 71.4 Ω  (internal coil resistance)
External R = 50 Ω (two 100 Ω in parallel: 49.8 Ω measured)   C = 0.1 μF
Total R = 50 + 71.4 = 121.4 Ω

ω₀ = 1/√(LC) = 1/√(0.1 × 10⁻⁷) = 1/√(10⁻⁸) = 10,000 rad/s
α = R/2L = 121.4/0.2 = 607 s⁻¹
Since α (607) << ω₀ (10000) → UNDERDAMPED ✓
Expected ringing freq: ω = √(ω₀²–α²) = √(10000²–607²) ≈ 9982 rad/s  → T ≈ 0.629 ms
6.	Series L–C–R on breadboard. Inductor first, then cap, then the parallel 100Ω pair.
7.	Gen: 10 Hz square wave, 4 Vpp, Hi-Z  (fast enough to see full ring-down before next edge)
8.	CH1 → gen output, CH2 → across the 50Ω resistor (not the whole circuit)
9.	Scope: triggered on CH1 falling edge. Could see the ringing! Took a video of the cursor moving.

## 2B
Swapped C = 0.1 μF → 47 μF  and R_ext = 50 Ω → 1 kΩ
Measured 1 kΩ with DMM: 998 Ω ✓.  R_total = 1000 + 71.4 = 1071.4 Ω
ω₀ = 1/√(0.1 × 47×10⁻⁶) = 1/√(4.7×10⁻⁶) = 461 rad/s
α = 1071.4 / (2×0.1) = 5357 s⁻¹
α >> ω₀ (5357 >> 461)  →  OVERDAMPED ✓
b = √(α²–ω₀²) = √(5357²–461²) = 5337 s⁻¹
Slow decay: D_slow = α–b = 5357–5337 = 19.9 s⁻¹  (τ_slow ≈ 50 ms)
Fast decay: D_fast = α+b = 5357+5337 = 10,694 s⁻¹  (τ_fast ≈ 0.09 ms — gone almost instantly)
So we should see just a simple-looking exponential decay on the slow timescale ✓