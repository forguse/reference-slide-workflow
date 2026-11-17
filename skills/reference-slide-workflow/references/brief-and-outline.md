# Brief to page-by-page outline

Read this before creating a new presentation. The saved outline is a working design document, not a generic list of section titles and not an extra slide in the deck. Write it in the user's language. Save it before authoring the pilot or page SVGs.

## Respond to the actual input

| Input | Action |
|---|---|
| A broad topic or vague goal | Read available materials first. Infer a useful audience, narrative and level of detail; record reasonable assumptions in the production document. Draft the full page sequence yourself. Ask only when an unresolved choice materially changes the task, such as pitching investors versus teaching beginners. |
| Detailed requirements without an outline | Extract hard constraints: scope, must-have topics, duration, page count, exact wording, visuals, sources and style. Organize these into a coherent page sequence, with each requirement mapped to pages or a deck-wide rule. Do not ask the user to write the outline. |
| An explicit user outline | Retain its structure, order, named sections and specified content. Add missing page messages, evidence, image choices and layout details. If expansion is allowed, split a crowded section or add a necessary bridge while explaining the change in the production document. Do not silently replace the outline with a preferred story. “Exactly follow this outline” prevents restructuring. |
| An existing presentation / project | Read the current outline if present. For content or structure changes, update the affected entries and requirement mapping. For alignment, color, spacing or a typo, edit the current source directly; no full outline rewrite. An older project without an outline does not need a fabricated historical plan to fix one page. |

Specific user instructions take precedence. If a fixed page count conflicts with specified content, propose a concrete compression or split; ask only if resolving it would violate a stated constraint. If the user requests an outline only, finish with the outline. If they request approval before production, wait at that checkpoint. Otherwise, provide a brief link to the saved outline and continue without routine approval.

## Required detail

The opening brief records audience, purpose, duration, page-count constraint, narrative, material permissions and assumptions. Preserve the difference between explicit user requirements and your proposed choices.

For **every page**, record:

1. Stable page ID, working title, page purpose and the one takeaway the audience should retain.
2. Concrete content: proposed on-slide claims, essential numbers/units/conditions and key wording. “Introduce the background” is not enough.
3. Evidence sources with usable locators: filename plus page/figure/table, data columns, or an authorized external source. Distinguish a proposed plan from an observed result.
4. Visual plan: what each image/chart/diagram depicts, its explanatory job, source or planned acquisition route, crop/panel choice and placement. If several figures form a set, state their count and relationship. An unresolved choice belongs in the production record; never write “find a suitable image” as the entire visual plan.
5. Composition: reading order, relative image/text areas, alignment anchors and grouping. Retain the reference's visual rules while adjusting the layout for the actual number of items. Do not invent arbitrary pixel coordinates before testing the layout.
6. Approximate speaking time, speaker emphasis and transition when it is a spoken presentation. For an untimed document, use `seconds: 0` and state that timing is not applicable.
7. The IDs of requirements covered by the page.

Text-only pages are allowed when they serve the content and user request. If the user requires an image on every page, map that as a deck-wide constraint and implement a meaningful visual on each page. Do not introduce stock photos or generated pictures merely to fill a quota under a closed-material policy.

## Keep one editable plan

Use `plan.json` as the compact editable source for the outline and production record. Run:

```sh
python scripts/plan_project.py write --plan authoring/plan.json
```

This writes `outline.md` and `materials-and-decisions.md` beside it. Their content is generated from the plan, so update the JSON rather than maintaining three divergent copies. A starter shape is in [plan.example.json](plan.example.json); replace its example content with the actual task before use. A plan-only request can instead be delivered directly as Markdown; a PPT build uses the structured record for checks.

Add `"plan":"plan.json"` to the authoring spec. Initialization retains the plan and both readable documents inside `project/`. A normal custom build requires the plan; a literal bundled-preset preview is exempt. An explicit user request to skip the outline is recorded in the spec as `"planning_waiver":"<the user's actual instruction>"`; it must not be invented to bypass planning.

On a content revision, edit `project/plan.json`, then run `plan_project.py write --plan <build>/project/plan.json` and refresh the existing build. Check changed pages against their revised plan. A global narrative change can justify a new structure; a local change cannot justify redesigning the deck.

## Review without putting the burden on the user

Before production, verify that required topics are covered, the order supports the intended argument, figures have a real purpose, and time/count constraints fit. If the talk is four minutes, allocate about 240 seconds across the actual pages, including any opening or closing pages within that scope; do not add unrelated cover/thanks pages automatically.

After production, compare each actual page with its plan, then inspect the full-deck rhythm. The script checks structure, requirement mapping, page order, allowed material routes and declared raster use. It cannot judge whether a claim follows from a paper or whether the narrative is compelling; the agent must perform those checks. Never report that a semantic check was automated when it was not.
