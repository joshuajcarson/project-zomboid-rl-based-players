-- Rendered-client helper (research), shipped inside RLBridge because the server's mod list is what the client reloads
-- after connecting (RLClient is gone by then). Does nothing unless <cache>/Lua/rl_client.txt exists.
local RL = {}
local function log(msg) print("RLCLIENT " .. msg) end
local function enabled()
    local ok, r = pcall(getFileReader, "rl_client.txt", false)
    if not ok or not r then return false end
    r:close()
    return true
end

-- After connecting, an account with no character lands on the creation screens: spawn select, profession/traits,
-- appearance. Accept the defaults on each, a short settle delay after it becomes visible, then the game loads.
local STEPS = {
    { "spawn",      function(MS) return MS.mapSpawnSelect, "nextButton" end },
    { "traits",     function(MS) return MS.charCreationProfession, "playButton" end },
    { "appearance", function(MS) return MS.charCreationMain, "playButton" end },
}
RL.seen = {}
function RL.createStep(MS)
    for _, st in ipairs(STEPS) do
        local name = st[1]
        local ok, panel, btn = pcall(st[2], MS)
        if ok and panel and not RL.seen[name .. "!"] and panel:isVisible() then
            RL.seen[name] = (RL.seen[name] or 0) + 1
            if RL.seen[name] == 1 then log("creation screen: " .. name) end
            if RL.seen[name] >= 45 and panel[btn] then
                RL.seen[name .. "!"] = true
                log("accepting " .. name)
                local ok2, err = pcall(function() panel[btn]:forceClick() end)
                if not ok2 then log("click failed on " .. name .. ": " .. tostring(err)) end
            end
            return
        end
    end
end


local function install()
    local MS = MainScreen.instance
    if not MS or RL.hooked or not enabled() then return end
    RL.hooked = true
    local old = MS.update
    MS.update = function(self)
        old(self)
        RL.createStep(MS)
    end
    log("creation hook installed")
end

Events.OnMainMenuEnter.Add(install)
if MainScreen and MainScreen.instance then install() end
