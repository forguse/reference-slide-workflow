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

Make this a **loss review**, not an inventory of features already present. A pilot can contain a serif, a cutout and a texture while losing the reference's compact annotation block, subject-bound title and generous quiet field. First describe those relationships in the reference; then inspect the result at the same apparent page size. List what became weaker or disappeared. A valid package and a fluent paragraph praising the result are not reasons to clear a missing defining relationship.

Before scaling, inspect a representative content page and any cover whose visual logic is materially different. Compare against the reference at matching apparent size. Ask: Where does the eye enter? What carries the visual weight? Which edges, crops and text/image relationships make the composition work? Did the new page retain these in an appropriate form? Is meaningful small text positioned with the same care as the large subject?

If a reference-defining relationship has disappeared, repair it before producing the rest. Retaining the palette while replacing all image integration with plain rectangular photo rows is a failed interpretation when integration was a core target. A plain photo row is appropriate when that is the reference's grammar or the content needs it and the adaptation preserves the intended character.

Record each target as `retained`, `adapted` or `failed`, with the inspected page and a concrete observation. An `adapted` result explains what changed for the new content and how the core relationship survives. Generic praise, a geometric pass, or a higher element count is not style evidence. Required targets marked failed block export.

## Version-bound review

New reference-led projects use `review_protocol: "reference-pair-v1"` (set by initialization). After the HTML passes, create a private comparison board with `python scripts/style_review.py compare --out <build> --reference <image> --page 1`. For a portfolio contact sheet, add `--crop X Y W H` to select the actual slide, excluding the surrounding mockup. The tool pairs that reference with the current rendered page at equal apparent canvas size. Inspect the pair for composition and the full-size originals for small type. These review images may contain private references; they are not public slide assets. Existing projects can opt into this protocol when their reference interpretation needs revision.

Record each target only after comparison. A result observation must say how it relates to the reference, an adaptation needs a content-based reason, and `remaining_gaps` lists missing defining relationships. An empty list means an actual loss review found none; it must not be prefilled as an approval shortcut. Unresolved gaps block export even when `status` says `adapted`. Record ordinary differences that preserve the design's purpose in the adaptation reason, not as invented defects.

Example review input:

```json
{"targets":[{"id":"subject-type-space","page":1,"status":"adapted","reference_observation":"The reference gathers its short reading text beside the subject and leaves the opposite field quiet.","observation":"The wider new subject meets a compact annotation block at its left edge; the opposite field remains open.","adaptation_reason":"The new subject is wider, so the annotation becomes horizontal while retaining its proximity and secondary visual weight.","remaining_gaps":[]}]}
```

Run `python scripts/style_review.py record --out <build> --file <review.json>`. The exporter requires this assessment alongside ordinary visual review. It binds the review to the profile, target page's visual digest and exact screenshot bytes; changed targets or page pixels require renewed inspection. Unchanged representative pages can retain evidence when other pages change.

The script checks comparison evidence, explicit gap disposition and freshness; it cannot certify aesthetic quality. The agent must actually compare and judge the images. Do not present this gate as an automated beauty score or a promise that every subjective preference has been anticipated. Preserve these working records outside the slides.
