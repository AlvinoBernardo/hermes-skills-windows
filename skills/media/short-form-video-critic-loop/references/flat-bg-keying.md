# Keying imagegen poses off a flat background

This is for generating characters and props on a flat colour (e.g. lavender #8D87AE) and compositing them as cutouts.

1. **Estimate the background** as the median of the TOP rows and the upper half of the left/right edges only. Full-figure poses touch the bottom edge, and sampling there produced thresholds in the hundreds that kept the whole frame.
2. **Set thresholds:** `t0 = max(6, p98(edge deviation)) * 1.2`, `t1 = 3.6 * t0`. Alpha = `clip((dist - t0)/(t1 - t0))`, applied only to bg-like regions connected to the border.
3. **Enclosed holes** (between legs, arm and tail) aren't border-connected. Also key large connected regions closer than `1.6*t0` (more than 400 px), dilated by 2 and limited to the bg mask.
4. **Clean up:**
   - Drop islands under 0.2% of the area.
   - Despill semi-transparent pixels with `(rgb - (1-a)*bg)/a`.
   - Remove the flat purple floor shadow in the bottom 14% (`B-R>18 and B-G>24`, valid when the subject has no purple).
   - Crop to the alpha bbox.
5. **Inspect every cutout on a dark contrasting sheet**: ears, tail tips, fingers, shoes, the gaps between limbs.

## Prop sprite sheets
- Ask for "3 columns x 2 rows with LARGE empty gaps, each item isolated".
- Key the whole sheet using all four edges as the bg sample. There is no figure touching the bottom here.
- Split by connected components, not by fixed grid cells:
  1. Take alpha > 60 and dilate about 12 px.
  2. Keep the 6 largest components.
  3. Order them by row (centre y vs H/2), then by x.
- Generated items routinely cross the nominal cell lines (bottles, bowls, spoons), and fixed cells chop them.
- Name the outputs `food-<item>.png` so the renderer can paste them by name.

## Pose prompts that pass
List the identity traits explicitly every time, then the pose, then the framing:
- **Identity:** "ONE cream-tipped tail, black-tipped ears, charcoal joggers…"
- **Pose:** whatever the shot needs.
- **Framing:** "Full body, ears to shoes fully in frame with generous margin, centered. Flat plain lavender background (RGB 141,135,174), no floor shadow, no text."

This produced 7/7 consistent poses with props (scale, salad bowl, frying pan + oil, burger, water jug).

## Identity consistency
Pass the approved character image as `image_url` for every pose. Check each pose's sheet for identity (ears, muzzle, single tail, outfit) and anatomy before use.

## Imagegen safety pitfall
Prompts for a shirtless character with a heavier or fat body, or tight medium shots of a shirtless muscular mascot, can be rejected as "sexual". Rephrase as "family-friendly cartoon mascot illustration", put the character in a plain t-shirt, and use full-body framing.
