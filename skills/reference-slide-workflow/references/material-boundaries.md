# Material boundaries and production decisions

Use the user's purpose and explicit instructions to set permissions. Do not infer permission from “science”, “humanities”, or “marketing” alone. A visual reference authorizes style analysis; it does not automatically authorize using its people, brands, facts or images in new content.

## Select a boundary before sourcing

Record three independent sourcing permissions in the plan: external factual sources, external images, and generated images. Separately record image-editing scope: allowed operations, protected content, and the instruction establishing permission. Permission to obtain or generate an image does not automatically authorize AI alteration of supplied evidence. Allow per-page or per-asset overrides only when supported by the user's instructions, with the reason recorded.

| User intent | Appropriate behavior |
|---|---|
| “Only use my materials; don't search or generate images” | Extract, crop safely, rearrange and explain supplied material. Faithful native redraws or charts from supplied data are allowed when they preserve labels, values, uncertainty and relationships. Do not invent new results, apparatus, data or factual claims. |
| “You may supplement with external sources” | Use the permitted source types and record their provenance and use rights. Permission to research facts does not itself permit image generation. |
| “Develop this concept; find or generate visuals” | Build original explanatory or promotional visuals within the authorized scope. Keep generated concepts distinguishable from real evidence in the material record and project context. Do not present generated measurements, experiments, real events or actual products as documentary evidence. |
| Permission is unclear and extra material is necessary | Ask one concise question about the missing permission. Continue work supported by existing material. Do not treat “more images” or a style reference as permission to source or generate. |

A project can combine boundaries: a product concept page may allow generation while an experimental evidence page remains closed. Explicit restrictions persist through revisions. A shortage of pictures never silently relaxes them.

## Process images according to their role

For each intended edit, consider the asset's role and the user's purpose before choosing a technique. Discipline alone is insufficient: a marketing deck can contain protected test results, and a scientific deck can contain a freely editable conceptual illustration.

| Asset and purpose | Default editing boundary |
|---|---|
| Measurements, plots, microscopy, scans, apparatus photos, documentary or other evidence | Preserve the source. Layout operations may scale proportionally or crop irrelevant outer whitespace when no information or context is lost. Keep axes, legends, labels, conditions and relevant surrounding evidence. Do not use generative fill, redraw, denoising, sharpening that invents detail, object removal, relighting, or color alteration that could change interpretation without specific authorization. |
| An authorized conceptual, editorial, decorative or promotional image | When the brief permits creative treatment, AI cutouts, background extension, selective cleanup, or tonal treatment may serve a specific composition need. State the intended operation in the working record; preserve protected identity, product features and factual meaning. Creative permission does not make an invented view of a real site into documentary evidence. |
| Unclear role, or an operation that may affect factual interpretation | Keep the original in the supported draft and ask about the concrete proposed change. Do not treat a desire for beauty, a shortage of images or general permission to generate as consent to alter evidence. |

Prefer native cropping, framing, masks or overlays when they solve the presentation need while retaining the original image. Use AI editing when it adds a useful capability, not merely because it is available. A protected photo can sit beside an independently created diagram without repainting the photo.

Never overwrite the original. Record the derivative's parent, actual edit, tool, prompt when applicable, source/derivative hashes and slide use; inspect before and after. Generative edits must be declared as generated/derived material and must not pass through as unchanged user evidence. For optional editable-image candidates, show the alternative separately or describe it in the production record; keep uncertainty out of slide copy. User-required and legally required disclosures still apply.

## Where uncertainties and sources belong

Write provenance, license/rights notes, generated-image records, alternatives and production questions in **materials-and-decisions.md**. They are not on-slide disclaimers. Do not add “素材不足”, “尚未核实”, “仅供参考”, “AI 生成示意” or a boundary legend to a slide merely because the production workflow has open questions. Where external law, platform requirements, a source license or the user actually requires a visible credit/disclosure, comply with that specific requirement; select a different asset if its required treatment conflicts with the requested presentation.

Preserve necessary scientific conditions, units, error bars, uncertainty ranges and qualifications in the content. These carry meaning. Do not conceal a misleading inference by moving its essential qualification into a hidden production note. A concept brief can define a fictional product clearly outside the deck; do not make it look like independently verified real-world performance.

For a missing fact or uncertain experiment interpretation central to the story, ask before using it as established fact. For noncritical visual alternatives, prepare concrete candidates or a complete supported draft, list the decisions separately and ask the user to choose or accept them together. A pending required decision stays pending until answered; elapsed time is not approval. A delivery depending on it remains a review draft, identified in the handoff/file naming rather than cluttering every slide.

## Record actual materials

Each source needs an ID, origin and a usable locator (file/page/figure or direct source URL), plus rights information for externally reused images. Each raster asset needs a source ID, SHA-256, purpose and status. A derived asset points to its parent source and describes the actual transformation. Generated assets record the creation brief and conceptual role. Notes alone do not make a copyrighted asset reusable.

The plan's visual list identifies which assets belong on each page. The build check compares the raster bytes actually embedded with the declared hashes, checks page-scoped permissions and refuses generated images used as evidence. Native charts and diagrams still need their data or factual source in the page plan; the agent checks their semantic fidelity.

The checks establish traceability and detect undeclared/disallowed assets. They do not independently authenticate a user statement, license, photograph or generated-image declaration. Inspect the original source and pixels when making those determinations.
