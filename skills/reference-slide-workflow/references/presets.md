# Optional presets

The user chooses a preset explicitly, or provides a reference. Presets are examples and starting points, not the scope of the workflow.

| Preset | Character | Useful page roles |
|---|---|---|
| `academic-blue` | Blue hierarchy, restrained gradients, pale background, compact native evidence | Research, project reviews, technical proposals |
| `editorial-light` | Warm paper background, dark ink, rust emphasis, typography-led covers, open rules | Strategy, teaching, editorial presentations |
| `structured-blue` | Pale diagonal field, blue gradients, dense figure zones, four-stage route and task matrix | Project proposals, technical reviews and structured reports |

The first two include six original, editable layouts: cover, transition, evidence, comparison, process and ending. Their example content is synthetic. The third adapts a user-authorized reference into nine editable layouts: cover, transition, problem comparison, four-stage route, task with figures, results, resources, plan and ending. It retains the reference's geometry, gradients and typography while removing identity and subject-specific content. Figure areas are native editable placeholders, ready for the user's own evidence. No real person, logo, campus photograph or private research figure is bundled.

To use your own material, copy the chosen preset's deck spec and profile into a project authoring directory, author the required pages and supply their contracts. Replace a figure placeholder group with the intended local raster or editable evidence, retaining its alignment relationships. Do not change package assets to solve one presentation. Add or remove page roles according to the requested count and narrative. A preset's demo page count does not impose a deliverable page count.

Run `make_presets.py --out <new-directory>` to reproduce the first two original neutral presets. The nine reference-derived SVG layouts are distributed directly under `assets/presets/structured-blue`. A reference with different colors, typography, density or aspect ratio should get its own style profile and page family.
