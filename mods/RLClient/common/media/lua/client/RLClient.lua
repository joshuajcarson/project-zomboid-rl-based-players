-- Rendered-client helper (research). Reads <cache>/Lua/rl_client.txt ("user|password|host|port[|hash 0/1]") and connects from the
-- main menu with the same call the multiplayer Join dialog makes, so no one has to click through the UI.
local RL = { frames = 0, done = false, hooked = false }

local function log(msg) print("RLCLIENT " .. msg) end

local function readCfg()
    local ok, r = pcall(getFileReader, "rl_client.txt", false)
    if not ok or not r then return nil end
    local line = r:readLine(); r:close()
    if not line then return nil end
    local f = {}
    for piece in string.gmatch(line, "[^|]+") do f[#f + 1] = piece end
    if #f < 4 then return nil end
    return { user = f[1], pass = f[2], host = f[3], port = f[4], hash = (f[5] ~= "0") }
end

local function install()
    local MS = MainScreen.instance
    if not MS or RL.hooked then return end
    RL.hooked = true
    local old = MS.update
    MS.update = function(self)
        old(self)
        if RL.done then return end
        RL.frames = RL.frames + 1
        if RL.frames < 120 then return end          -- let the menu settle first
        local c = readCfg()
        if not c then RL.done = true; log("no rl_client.txt, not connecting"); return end
        RL.done = true
        log("connecting as " .. c.user .. " to " .. c.host .. ":" .. c.port)
        local ok, err = pcall(function()
            ConnectToServer.instance:connect(MS, "", c.user, c.pass, c.host, "", c.port, "", false, c.hash, 1)
        end)
        if not ok then log("connect failed: " .. tostring(err)) end
    end
    log("main menu hook installed")
end

Events.OnMainMenuEnter.Add(install)
log("RLClient loaded")
