# Optional presets

The user chooses a preset explicitly, or provides a reference. Presets are examples and starting points, not the scope of the workflow.

| Preset | Character | Useful page roles |
|---|---|---|
| `academic-blue` | Blue hierarchy, restrained gradients, pale background, compact native evidence | Research, project reviews, technical proposals |
| `editorial-light` | Warm paper background, dark ink, rust emphasis, typography-led covers, open rules | Strategy, teaching, editorial presentations |

Each includes six original, editable layouts: cover, transition, evidence, comparison, process and ending. Their example content is synthetic. No school, business, real person, logo, campus photograph or private research figure is bundled.

To use your own material, copy the chosen preset's deck spec and profile into a project authoring directory, author the required pages and supply their contracts. Do not change package assets to solve one presentation. Add or remove page roles according to the requested count and narrative. The preset's six-page demo does not impose a six-page deliverable.

Run `make_presets.py --out <new-directory>` to reproduce the original neutral assets. A reference with different colors, typography, density or aspect ratio should get its own style profile and page family, rather than being squeezed into either preset.
