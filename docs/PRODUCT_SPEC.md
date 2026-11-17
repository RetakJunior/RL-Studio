# RL Studio product direction

## Product decision

RL Studio is planned as a downstream digital painting application built from the Krita source tree in this workspace. Krita's existing canvas, document, layer, brush, tablet, color, and plugin systems are the product foundation. This is not a clean-room application or a plan to replace Krita's engine.

The current source still identifies itself as Krita in many user-visible and packaging surfaces; it is not yet an RL Studio release. Preserve upstream attribution and license notices. Use Clip Studio Paint only as a workflow reference, not as a source of protected visual expression or assets.

## Product intent

Give illustrators and digital artists a stable, canvas-first desktop workspace with professional painting tools, predictable document handling, efficient input, and a coherent RL Studio identity.

## Principles

- Reuse mature Krita behavior where it meets the goal; extend it with small, testable changes.
- Protect artwork and existing file compatibility.
- Do not expose controls for behavior that is not implemented.
- Measure input/render behavior before making performance claims.
- Treat branding, packages, resources, translations, and legal notices as a coherent downstream layer.

## Scope and acceptance

No RL Studio feature release is established. First preserve the existing Krita workflows, define an accurately attributed product identity, and select a focused improvement from user needs and measured data. Keep file formats and painting behavior compatible unless a migration plan is tested. New changes need a reproducible build and relevant test; UI work also needs interaction review. A title or color change alone is not a finished rebrand.
