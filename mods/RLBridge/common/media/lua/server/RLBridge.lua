-- Observes every online player (fake clients are real IsoPlayers on the server) and prints "RLOBS" lines.
-- Also runs a one-shot action test: gives each new player an axe and reports the inventory change.
local OBS_EVERY, RADIUS = 60, 15
local ticks, given = 0, {}

local function log(msg) print("RLBRIDGE " .. msg) end

local failed = {}
local function try(name, f)
    local ok, v = pcall(f)
    if ok and v ~= nil then return v end
    if not failed[name] then failed[name] = true; log("getter failed: " .. name .. " (" .. tostring(v) .. ")") end
    return -1
end

local function observe(p)
    local cell = getCell()
    local near, nearest = 0, 9999
    local zl = cell:getZombieList()
    for i = 0, zl:size() - 1 do
        local z = zl:get(i)
        local d = math.sqrt((z:getX() - p:getX()) ^ 2 + (z:getY() - p:getY()) ^ 2)
        if d <= RADIUS then near = near + 1 end
        if d < nearest then nearest = d end
    end
    local function stat(statName) return try("stat." .. statName, function() return p:getStats():get(CharacterStat[statName]) end) end
    return string.format(
        '{"user":"%s","x":%.1f,"y":%.1f,"z":%d,"health":%.1f,"hunger":%.3f,"thirst":%.3f,"fatigue":%.3f,"items":%d,"zombiesNear":%d,"nearestZombie":%.1f,"kills":%d}',
        try("username", function() return p:getUsername() end), p:getX(), p:getY(), p:getZ(),
        try("health", function() return p:getBodyDamage():getHealth() end),
        stat("HUNGER"), stat("THIRST"), stat("FATIGUE"),
        try("items", function() return p:getInventory():getItems():size() end),
        near, nearest, try("kills", function() return p:getZombieKills() end))
end

Events.OnTick.Add(function()
    ticks = ticks + 1
    if ticks % OBS_EVERY ~= 0 then return end
    local players = getOnlinePlayers()
    if not players then return end
    for i = 0, players:size() - 1 do
        local p = players:get(i)
        local ok, res = pcall(observe, p)
        log("RLOBS " .. (ok and res or ("error " .. tostring(res))))
        local name = p:getUsername()
        if not given[name] then
            given[name] = true
            local before = p:getInventory():getItems():size()
            local ok2, err = pcall(function() p:getInventory():AddItem("Base.Apple") end)
            log("RLACT give Apple to " .. name .. " ok=" .. tostring(ok2) .. " " .. tostring(err or "") ..
                " items " .. before .. " -> " .. p:getInventory():getItems():size())
        end
    end
end)
log("RLBridge loaded")
