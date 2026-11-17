# UI and interaction direction

## Existing baseline

Krita already provides a desktop painting shell with XMLGUI menus/actions, toolbars, dockers, workspaces, canvas navigation, configurable shortcuts, tablet/input profiles, and dark/light themes. RL Studio should retain professional desktop density and canvas priority while establishing its own identity deliberately.

## Design rules

- Preserve functional density and dockable panels; do not replace the workspace with generic cards or a web dashboard.
- Keep canvas navigation, brush controls, layer visibility, document state, and errors discoverable.
- Prefer existing Qt/KDE widgets and theme conventions over a parallel UI toolkit.
- Make focus, selection, disabled/error states, high-DPI sizing, and tablet/mouse interaction consistent.
- Use original or properly licensed assets for new RL Studio branding; retain notices for inherited assets.
- Do not promise features unless implementation and behavior are verified.

## Validation

Review actual workflows: launch, open a document, change tools, draw, move/resize dockers, save, reopen, and inspect unsaved/error states. Compare screenshots at representative sizes/scales. Compilation alone does not establish UX quality.

No source build or interactive review has been completed here. An installed Krita 5.3.4.1 binary is separate from this source snapshot and is not a runtime baseline for it.
