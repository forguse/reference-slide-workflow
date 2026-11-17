# Revisions without redesign

## One source of truth

For an authored project, `project/svg_output`, `project/images`, `project/notes`, `style-profile.json` and `layout-contracts.json` are the source. HTML is a preview and PPTX is an exported result. For a presentation edited manually after export, the latest PPTX becomes the source and must enter official native editing. The wrapper detects an altered last-exported PPTX and refuses to overwrite it from stale SVGs.

Change only the necessary objects and their layout relationships. A text change may need a different wrap; a moved caption may require its group or text frame to move. It does not justify reinitializing all pages. Use a new filename for the revised PPTX and preserve the original.

```sh
python scripts/build_html.py --out work/my-deck --refresh
```

This refresh preserves SVG bytes, ordering, notes and assets. It repackages HTML and updates version hashes. It does not regenerate a layout from the preset.

## Version-bound patches

```json
{
  "base_digest":"Copy from the current build.json",
  "reason":"Update the title while retaining the reference style",
  "edits":[{
    "page":1,"id":"p1-main-title",
    "expect":{"text":"Current title"},"text":"Revised title"
  }]
}
```

```sh
python scripts/revise_project.py --out work/my-deck --patch patch.json --dry-run
python scripts/revise_project.py --out work/my-deck --patch patch.json
```

All old-value checks run before writes. Changes are backed up, and only listed pages are written. Plain text patches cannot silently replace rich color spans. Use explicit `runs`, or `lines` with `leading`. Keep data-pptx-frame and related converter metadata coherent with object geometry. Add images inside the project and update their provenance before refreshing.

## Three checks owned by the agent

1. Geometry and fonts: run on every page after every refresh, including transformed bounds, containment, alignment cohorts, spacing, collisions and text-crossing lines.
2. HTML: inspect all pages initially. On a revision, inspect pending pages and the overall deck rhythm. Judge optical alignment, figure whitespace and density.
3. Actual PPTX: verify the exported package and inspect rendered pages. HTML success does not prove that native PowerPoint text frames will render correctly.

The review gate records observations against actual screenshot hashes. Changes invalidate the affected review evidence; a numeric pass is never automatically recorded as visual approval. The current delivery report must pass before handoff. The user is not asked to do the agent's layout QA.

## Safe optimization

Retain the saved outline with the project. For changed facts, visuals, narrative or page order, update only the affected `project/plan.json` entries, regenerate the two readable documents with `plan_project.py write`, then refresh. Formatting changes do not require an outline rewrite. Plan changes are part of the build manifest but do not invalidate unchanged page pixels; material permissions are checked again at export. Older decks can receive a local fix without inventing a retrospective full outline.

HTML screenshots are reused only when page inputs, contracts, profile, browser/font measurements, checker versions and screenshot bytes match. PPT screenshots depend on the actual native slide, media, master/theme dependencies, renderer/fonts and screenshot bytes. Notes do not invalidate unchanged pictures, but exported notes and file hashes are still checked.

PPTX is still packaged completely by the official converter. That is not a redesign. Avoid fragile manual ZIP splicing merely to save packaging time. Speed gains come from retaining authored sources, editing a small set of objects and reusing proven unchanged renders.

## Common failures and their owning layer

| Symptom | Fix at the owning layer |
|---|---|
| Figure and prose look uneven despite equal y values | Inspect image whitespace and glyph bounds; align visible edges |
| Text is inside the slide but outside its module | Add the intended container contract; rewrite or restructure content |
| White text disappears at a gradient endpoint | Preserve a sufficiently dark endpoint; inspect actual contrast |
| Line crosses a navigation label | Separate line and label rows, or add an actual opaque plate |
| HTML is fine but PPT has corner text or collapsed frames | Inspect native extents and converter text metadata, then fix the source |
| A cutout is correct in HTML but its photograph shifts inside the PPT silhouette | Compare picture frame, source crop and visible geometry bounds. Use the converter's supported native crop representation to keep them consistent; zero-area registration points are not a verified fix. Re-render the actual target app. |
| A licensed display font works in HTML but becomes another CJK face in PPT | Inspect exported East Asian font mapping, not only installed fonts. Correct the specific mapping and verify the actual app render. |
| A small edit recreates the entire deck | Keep the project and refresh it; do not reinitialize |
| A “passed” record survives changed content | Bind reviews to source and screenshot hashes |
| Cache misses on every new process | Exclude transient environment paths; use stable font inventories |

New failures should produce a focused regression case, not an ever-growing universal restriction on design.

For native image silhouettes, a project may need an explicit source crop whose picture frame matches the visible silhouette bounds. Follow the pinned converter's crop-wrapper contract rather than inventing unsupported SVG attributes. Nested crop SVGs remain part of the same slide; browser checks must select the outer slide SVG, not mistake every nested SVG for another canvas. Keep a rendered example that exercises the exact failed case.
