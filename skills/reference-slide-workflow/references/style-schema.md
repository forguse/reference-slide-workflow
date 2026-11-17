# Style profile and authoring spec

`style-profile.json` is project-specific. Size values are SVG units; PowerPoint points are obtained through conversion, not by relabeling the same number.

```json
{
  "schema": 1,
  "name": "Custom reference style",
  "canvas": [1280, 720],
  "language": "en-US",
  "typography": {
    "title": {"family":"Arial", "size":42, "weight":700},
    "body": {"family":"Arial", "size":24, "weight":400},
    "caption": {"family":"Arial", "size":18, "weight":400}
  },
  "palette": {"background":"#FFFFFF", "ink":"#162433", "accent":"#275E88"},
  "margins": {"left":64,"right":64,"top":48,"bottom":40},
  "fixed_anchors": ["Title and body share the left edge"],
  "flexible_compositions": ["Figure with prose", "Three-stage process"],
  "identity_assets": [],
  "evidence": [{"source":"reference.png","region":"title","observation":"Bold sans-serif","confidence":"medium"}]
}
```

These values illustrate the schema; they are not defaults for all slides. Use the reference's real aspect ratio and visual hierarchy. All authored SVG viewBoxes must match the profile.

An authoring spec supplies the profile, actual SVGs and intended relationships:

```json
{
  "title":"A reference-based presentation",
  "plan":"plan.json",
  "profile":"style-profile.json",
  "slides":[{
    "id":"evidence",
    "name":"Evidence and interpretation",
    "svg":"pages/evidence.svg",
    "notes":"Source and interpretation of the figure.",
    "image_sources":{"figure":"Original source URL or user-provided file"},
    "contract":{
      "rules":[
        {"kind":"align","items":["figure","body-heading"],"edge":"top","tolerance":2},
        {"kind":"align","items":["body-heading","body-text"],"edge":"anchorX","tolerance":1},
        {"kind":"gap","items":["figure","caption"],"axis":"y","min":12,"max":24},
        {"kind":"inside","items":["body-text"],"box":[740,210,470,360]}
      ],
      "allow_overlap":[],
      "review_focus":["Visible figure top edge, not just the image box"]
    }
  }]
}
```

SVG nodes used in contracts need stable IDs. Initialization prefixes them per page to prevent duplicate IDs in a multi-page HTML document; the build manifest identifies final sources. If optical top alignment needs compensation, `align.offsets` may contain measured per-element offsets. Explain the cause. Do not enlarge tolerances until a bad page passes.

Supported rules are `align`, `inside`, `gap`, `equal-gap`, and `avoid`. Alignment edges include left/right/top/bottom/centerX/centerY/anchorX/baseline/width/height. `allow_overlap` requires an exact pair of IDs and a reason (e.g. an intentional image annotation). Empty contracts fail the checker. Contracts are authored design intent, never automatically learned from an unchecked draft.
## Native group bounds

For the pinned PPT Master final-page export, every visible top-level SVG group declares `data-pptx-bounds="x y width height"` in root-canvas coordinates. Keep the declared area synchronized when changing a figure group. A group around an editable placeholder needs this declaration too. HTML can look correct without it, but the official final export gate will reject the page. Metadata-only fixes still require a refreshed manifest and current review evidence; matching screenshot hashes can prove an already inspected image is unchanged.
