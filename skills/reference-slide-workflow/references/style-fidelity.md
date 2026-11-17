# Preserve the reference's design relationships

Use this for reference-led design, before the pilot and again while inspecting it. The default task is one coherent reference-led deck. A multi-style capability showcase is a separate user request, not the default behavior.

## Identify the decisions that carry the style

Find the few concrete relationships that make the reference recognizable. Color and font names alone are insufficient. Look for subject scale and silhouette, where image boundaries meet whitespace, crop and focal direction, how type attaches to or avoids a subject, contrast between display and marginal text, material treatment, layering, and the sequence of dense and quiet pages. Select what is actually present; do not impose this whole list on every reference.

Apparently simple pages may depend on precise crop, optical spacing, controlled asymmetry, weight contrast and one carefully chosen image. Preserve that precision. Complexity is not a quota of objects, effects, textures, fonts or photographs. Adding decoration does not repair a lost relationship.

Write project-specific `style_targets` in the profile. Each target needs a stable `id`, a reference region, an observable relationship and the page numbers where it must be tested. Use specific language: “the building silhouette enters the title's whitespace, while the small vertical note follows its edge” is assessable; “premium and sophisticated” is not.

Distinguish the recognizable design rule from the source's particular expression. Compose new words, subjects and proportions. Do not copy a unique arrangement of lettering, assets and ornament wholesale. When new content changes the number or orientation of pictures, preserve hierarchy and image/type logic while changing the composition.

## Resolve the intended relationship to the reference

Record `reference_mode` as `single` (one governing visual language), `synthesis` (a coherent original language informed by several references), or `showcase` (distinct series explicitly requested by the user). Several reference files do not imply a showcase. A synthesis must retain selected expressive decisions rather than reducing all references to their least distinctive common denominator.

## Extend a sparse reference into a page family

One supplied layout is a sample of the visual language, not a compulsory master for every page. Separate invariants (type relationships, image treatment, edge language, color roles and characteristic whitespace) from variables (figure count, orientation, hierarchy, reading direction, text amount and page job). Record measured observations separately from inferred extension rules in the working profile.

Inventory the new content before selecting layouts. For each page, identify its actual relationship: one subject with explanation, equal comparison, whole/detail, sequence, evidence, or closing. Choose a composition that expresses that relationship while retaining the invariants. One landscape photo becoming four figures may require unequal tracks for whole/detail or a shared-scale grid for comparison; preserve the reference's visual language instead of copying its original column count.

With few references, test an adapted content page that meaningfully differs from the supplied layout when the material calls for it. Inspect the reference and the family overview: do they share a recognizable character, and does each composition fit its content? Avoid both repetitive A-layout reskins and unrelated-looking pages. Repeated page jobs may legitimately reuse a layout; do not impose a minimum number of layout types or prohibit adjacent repeats.

With a diverse reference deck, inspect its existing families first and reuse/adapt them before inventing new ones. When an exact-layout instruction is explicit, follow it. With a single screenshot, derive additional compositions honestly; do not claim that inferred pages were present in the source. Optional per-page working fields: `page_job`, `content_relationship`, `layout_family`, `preserved_anchors`, and `adaptation_reason`.

## Test the hardest representative page

Before scaling, inspect a representative content page and any cover whose visual logic is materially different. Compare against the reference at matching apparent size. Ask: Where does the eye enter? What carries the visual weight? Which edges, crops and text/image relationships make the composition work? Did the new page retain these in an appropriate form? Is meaningful small text positioned with the same care as the large subject?

If a reference-defining relationship has disappeared, repair it before producing the rest. Retaining the palette while replacing all image integration with plain rectangular photo rows is a failed interpretation when integration was a core target. A plain photo row is appropriate when that is the reference's grammar or the content needs it and the adaptation preserves the intended character.

Record each target as `retained`, `adapted` or `failed`, with the inspected page and a concrete observation. An `adapted` result explains what changed for the new content and how the core relationship survives. Generic praise, a geometric pass, or a higher element count is not style evidence. Required targets marked failed block export.

## Version-bound review

For new reference-led projects, the authoring profile contains `reference_mode` and nonempty `style_targets`. After viewing the actual HTML screenshots, save a review input JSON:

```json
{"targets":[{"id":"subject-type-space","page":1,"status":"adapted","observation":"The new roof silhouette occupies the lower image field; the vertical annotation follows its left edge, with the primary title in the upper quiet field. The new wider subject changes the crop while retaining this relationship."}]}
```

Run `python scripts/style_review.py record --out <build> --file <review.json>`. The exporter requires this assessment alongside ordinary visual review. It binds the review to the profile, target page's visual digest and exact screenshot bytes; changed targets or page pixels require renewed inspection. Unchanged representative pages can retain evidence when other pages change.

The script checks completeness and freshness, not aesthetic quality. The agent must actually compare the reference and rendered result and make the judgment. Preserve these working records outside the slides; do not turn them into on-slide production explanations.
