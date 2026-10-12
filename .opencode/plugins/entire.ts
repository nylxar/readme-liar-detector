// Entire CLI plugin for OpenCode — plain-JS variant (no TS syntax at all).
// Context: Entire 0.11.4 ships V1-shaped TS; this workspace's opencode v2
// loader reported `Missing key at ["default"]` for every TS-annotated variant
// (refs err_dc75835d, err_575ab76e in opencode.log), so this file uses only
// runtime JS: default { id, setup }. Logic mirrors upstream Entire 0.11.4.
// Upstream original kept at ../entire-upstream/entire.ts for reference.
import { spawn, spawnSync } from "node:child_process"

async function EntireSetup(ctx) {
  const directory = ctx.directory
  const seenUserMessages = new Set()
  let currentSessionID = null
  let currentModel = null
  const messageStore = new Map()
  let pendingInjection = null

  function hookCmd(hookName) {
    return ["sh", "-c", "if ! command -v entire >/dev/null 2>&1; then exit 0; fi; exec entire hooks opencode " + hookName]
  }

  async function callHook(hookName, payload) {
    try {
      const json = JSON.stringify(payload)
      const parts = hookCmd(hookName)
      const cmd = parts[0]
      const args = parts.slice(1)
      await new Promise(function (resolve) {
        const proc = spawn(cmd, args, { cwd: directory, stdio: ["pipe", "ignore", "ignore"] })
        proc.on("error", function () { resolve() })
        proc.on("close", function () { resolve() })
        if (proc.stdin) proc.stdin.end(json + "\n")
      })
    } catch (e) { /* never crash OpenCode */ }
  }

  function callHookSync(hookName, payload) {
    try {
      const json = JSON.stringify(payload)
      const parts = hookCmd(hookName)
      const cmd = parts[0]
      const args = parts.slice(1)
      spawnSync(cmd, args, { cwd: directory, input: json + "\n", stdio: ["pipe", "ignore", "ignore"] })
    } catch (e) { /* never crash OpenCode */ }
  }

  function parseInjectedContext(stdout) {
    if (!stdout) return null
    const lines = stdout.split("\n")
    for (let i = 0; i < lines.length; i++) {
      const trimmed = lines[i].trim()
      if (!trimmed.startsWith("{")) continue
      try {
        const parsed = JSON.parse(trimmed)
        if (typeof parsed.inject_context === "string" && parsed.inject_context.length > 0) return parsed.inject_context
      } catch (e) { /* not our envelope */ }
    }
    return null
  }

  function fireTurnStart(payload) {
    try {
      const json = JSON.stringify(payload)
      const parts = hookCmd("turn-start")
      const cmd = parts[0]
      const args = parts.slice(1)
      const proc = spawnSync(cmd, args, { cwd: directory, input: json + "\n", encoding: "utf8", stdio: ["pipe", "pipe", "ignore"] })
      const out = typeof proc.stdout === "string" ? proc.stdout : ""
      const injected = parseInjectedContext(out)
      if (injected) pendingInjection = injected
    } catch (e) { /* never crash OpenCode */ }
  }

  function resetSessionTracking(sessionID) {
    if (currentSessionID === sessionID) return false
    seenUserMessages.clear()
    messageStore.clear()
    currentModel = null
    currentSessionID = sessionID
    pendingInjection = null
    return true
  }

  return {
    "experimental.chat.system.transform": async function (_input, output) {
      if (pendingInjection && Array.isArray(output.system)) {
        output.system.push(pendingInjection)
        pendingInjection = null
      }
    },
    event: async function (evt) {
      try {
        const event = evt.event
        switch (event.type) {
          case "session.created": {
            const session = event.properties && event.properties.info
            if (!session || !session.id) break
            if (resetSessionTracking(session.id)) {
              await callHook("session-start", { session_id: session.id })
            }
            break
          }
          case "message.updated": {
            const msg = event.properties && event.properties.info
            if (!msg) break
            if (msg.sessionID && resetSessionTracking(msg.sessionID)) {
              callHookSync("session-start", { session_id: msg.sessionID })
            }
            messageStore.set(msg.id, msg)
            if (msg.role === "assistant" && msg.modelID) currentModel = msg.modelID
            if (msg.role === "user" && !seenUserMessages.has(msg.id)) {
              seenUserMessages.add(msg.id)
              const sessionID = msg.sessionID ? msg.sessionID : currentSessionID
              if (sessionID) fireTurnStart({ session_id: sessionID, prompt: "", model: currentModel ? currentModel : "" })
            }
            break
          }
          case "message.part.updated": {
            const part = event.properties && event.properties.part
            if (!part || !part.messageID) break
            const msg = messageStore.get(part.messageID)
            if (msg && msg.role === "user" && part.type === "text" && !seenUserMessages.has(msg.id)) {
              seenUserMessages.add(msg.id)
              const sessionID = msg.sessionID ? msg.sessionID : currentSessionID
              if (sessionID) fireTurnStart({ session_id: sessionID, prompt: part.text ? part.text : "", model: currentModel ? currentModel : "" })
            }
            break
          }
          case "session.status": {
            const props = event.properties
            if (!props || !props.status || props.status.type !== "idle") break
            const sessionID = props.sessionID ? props.sessionID : currentSessionID
            if (!sessionID) break
            callHookSync("turn-end", { session_id: sessionID, model: currentModel ? currentModel : "" })
            break
          }
          case "session.compacted": {
            const sessionID = event.properties && event.properties.sessionID
            if (!sessionID) break
            await callHook("compaction", { session_id: sessionID })
            break
          }
          case "session.deleted": {
            const session = event.properties && event.properties.info
            if (!session || !session.id) break
            seenUserMessages.clear()
            messageStore.clear()
            currentSessionID = null
            pendingInjection = null
            callHookSync("session-end", { session_id: session.id })
            break
          }
          case "server.instance.disposed": {
            if (!currentSessionID) break
            const sessionID = currentSessionID
            seenUserMessages.clear()
            messageStore.clear()
            currentSessionID = null
            pendingInjection = null
            callHookSync("session-end", { session_id: sessionID })
            break
          }
        }
      } catch (e) { /* never crash OpenCode */ }
    }
  }
}

export default {
  id: "entire",
  setup: EntireSetup
}
