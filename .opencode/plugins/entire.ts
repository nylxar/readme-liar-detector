// Compat wrapper: Entire 0.11.4 generates a NAMED export (EntirePlugin),
// but this workspace's opencode loader requires a DEFAULT definition with
// an id and an effect or setup function (err_dc75835d). Re-export upstream
// untouched from ../entire-upstream/entire.ts so `entire agent add opencode
// --force` can still refresh it. Reversible: delete this file, move upstream
// back to plugins/entire.ts.
import { EntirePlugin } from "../entire-upstream/entire"

export default {
  id: "entire",
  setup: EntirePlugin,
}
