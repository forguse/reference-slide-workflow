# Runtime and commands

Use host-discovered runtimes; never copy another user's absolute machine paths. Requirements: Python 3.12+, Node 20+, Playwright with a Chromium browser, and the reference's fonts. Image/PDF inspection additionally uses Pillow/PyMuPDF. The examples use `python` and `node` as placeholders for the host's actual executables.

## Initialize a new project

Explicit preset selection:

```sh
python scripts/build_html.py --preset academic-blue --out work/example
```

Custom reference-based pages:

```sh
python scripts/inspect_reference.py reference.pptx --out private/reference-evidence.json
python scripts/plan_project.py write --plan authoring/plan.json
python scripts/build_html.py --spec authoring/deck.json --out work/my-deck
```

Write the page plan before authoring SVGs; the command saves the readable Markdown outline and material/decision record. The authoring spec points to `plan.json`, `style-profile.json`, authored SVGs, notes and layout contracts. See [brief and outline planning](brief-and-outline.md) and [style schema](style-schema.md). An image reference requires actual visual inspection; the inspector is evidence collection, not an automatic style copier. Repeated initialization of an existing directory is refused.

New custom projects require a plan unless the user explicitly waives it. Literal bundled-preset previews and existing older projects remain supported. Refresh verifies page order, current planning documents and declared image bytes. Export also rejects unresolved required material decisions. The scripts do not decide whether a scientific interpretation is correct.

## Preview and inspect

```sh
node scripts/render_check.cjs --out work/my-deck --playwright-module /path/to/node_modules/playwright --channel msedge
python scripts/review_gate.py pending --out work/my-deck --stage html
```

On other platforms use a locally installed Chromium or appropriate Playwright channel. After actually viewing the screenshots, record observations using `review_gate.py record --stage html --pages 1,2 --observation "Specific observations from the inspected images"`. Do not invent inspection records. An accepted font substitution must be explicit and remains marked in the report.

If the user requests only an HTML preview, finish with `review_gate.py finalize-preview --out work/my-deck`. Its report explicitly says `ppt_verified: false`. Full PPT delivery still requires both stages. The preview language follows the profile and Chinese profiles get Chinese navigation labels.

Reference-led projects additionally compare the actual reference and representative pages against the profile's `style_targets`, then record `python scripts/style_review.py record --out work/my-deck --file style-assessment.json`. See [style fidelity](style-fidelity.md) for the observation format. Missing, failed or stale target evidence blocks preview finalization and PPT export; ordinary geometry approval cannot replace it.

New projects use `reference-pair-v1`: first run `python scripts/style_review.py compare --out work/my-deck --reference private/reference.png --page 1` (optionally `--crop X Y W H` for a contact sheet), inspect the generated board and full-size pages, and then record reference observations, adaptation reasons and any remaining gaps. Open gaps and stale comparison images block approval. These private comparison images are review evidence, not slides or public examples.

## Official conversion dependency

PPT Master is fetched separately, at the immutable version in dependency-lock.json:

```sh
python scripts/fetch_ppt_master.py --dest vendor/ppt-master
```

Read its SKILL.md, run its attribution guard, and read its routing authority before choosing the appropriate official route. This package's export wrapper is for already-authored canonical SVG projects and uses its quick conversion interface. When a user asks for native PPTX editing, use the official native route, not this generation wrapper. Preserve upstream notices and checks. A local task's authorization determines whether a user checkpoint is already satisfied.

```sh
python scripts/export_pptx.py --out work/my-deck --ppt-master vendor/ppt-master --pptx work/my-deck/result-v1.pptx
```

The wrapper rejects stale sources/reviews, checks the pinned converter identity, runs upstream quality checks and preserves intermediate directories. It verifies slide order, aspect ratio, relationships, text readback, notes count and suspiciously tiny native text frames.

## Verify the actual PPTX

With a host-provided Artifact Tool module:

```sh
node scripts/render_pptx.mjs --out work/my-deck --artifact-module /path/to/@oai/artifact-tool/dist/artifact_tool.mjs
python scripts/review_gate.py pending --out work/my-deck --stage ppt
python scripts/review_gate.py record --out work/my-deck --stage ppt --pages 1,2 --observation "Specific observations from the actual PPT render"
python scripts/review_gate.py finalize --out work/my-deck
```

The Artifact Tool module is host-provided, not bundled or assumed to be a public npm install. If unavailable, use `record_external_render.py` with PNGs exported by PowerPoint or another available renderer. It hashes the actual PPTX and each screenshot into the same review process; do not substitute HTML screenshots for PPT renders. Runtime availability must be checked before claiming the export is visually verified.

Optional extra font locations use `PPT_FONT_DIRS`, separated by the platform path separator. The check records stable system/user font directories rather than transient process paths.
