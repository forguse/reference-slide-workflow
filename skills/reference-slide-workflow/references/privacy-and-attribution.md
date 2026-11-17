# Public packaging and attribution

Keep private generation work separate from a public release tree. Publish an explicit allowlist of intended files. Start a new public repository from the sanitized tree; never publish a repository that still contains private content in its history.

Inspect visible text, slide notes, document properties, hidden pages, alt text, comments, hyperlinks, media names, embedded objects, thumbnails and the actual pixels in images. A logo, building or paper figure can identify an organization even after its name is removed. Replace identity-bearing images with original neutral content; do not merely blur a few characters and claim anonymization.

Do not copy raw conversations, screenshots of private apps, usernames, local machine paths, research manuscripts or user-specific validation logs into a public package. Keep a private denylist outside the release tree to check project-specific names and identities without publishing that list.

```sh
python scripts/privacy_audit.py public-tree --deny-file private/privacy-denylist.txt --media-review private/media-review.json --report private/privacy-report.json
```

The audit searches text and Office ZIP parts and lists raster assets that need visual inspection. A media review maps each listed relative path to its SHA-256 and a concrete observation after viewing. Pixel inspection and a source/license inventory are required; a text scan alone cannot certify anonymity. The audit does not upload files or confer permission to publish them.

Preserve third-party licenses and attribution. This repository's original neutral presets are covered by its license; user references and third-party images are not. The converter's official copyright and sponsor notices remain intact. Do not remove provenance to make a package appear wholly original.
