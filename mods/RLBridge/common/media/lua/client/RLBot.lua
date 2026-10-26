-- Rendered-client bot (research): executes the same actions the fake-client env uses (goto, stop, attack, equip) on the
-- local player, driven by server commands "bot|user|cmd|a|b|c" from RLBridge. Idle unless commands arrive.
local RL = { target = nil, pathed = false, sentAt = 0 }
local function log(msg) print("RLBOT " .. msg) end

local function localPlayer()
    local ok, p = pcall(getPlayer)
    if ok then return p end
end

local function nearestZombie(p, maxDist)
    local best, bd = nil, maxDist
    local list = getCell():getZombieList()
    for i = 0, list:size() - 1 do
        local z = list:get(i)
        if not z:isDead() then
            local d = math.sqrt((z:getX() - p:getX()) ^ 2 + (z:getY() - p:getY()) ^ 2)
            if d < bd then best, bd = z, d end
        end
    end
    return best, bd
end

local function equip(p, itemType)
    local short = string.gsub(itemType, "^Base%.", "")
    local item = p:getInventory():getFirstTypeRecurse(short)
    if not item then return false, "no item " .. short end
    p:setPrimaryHandItem(item)
    if item:isRequiresEquippedBothHands() then p:setSecondaryHandItem(item) end
    return true
end

local commands = {}
-- bot|user|reload : run <cache>/Lua/rl_bot_dev.lua (research iteration without a server restart; the server checksums
-- client Lua at boot, so edits to this file itself need one). The file gets (RL, commands, log) and may override both.
function commands.reload(p)
    local r = getFileReader("rl_bot_dev.lua", false)
    if not r then return false, "no rl_bot_dev.lua" end
    local lines = {}
    local line = r:readLine()
    while line do lines[#lines + 1] = line; line = r:readLine() end
    r:close()
    local f, err = loadstring(table.concat(lines, "\n"))
    if not f then return false, tostring(err) end
    f(RL, commands, log)
    return true, "reloaded"
end
local function walking(p)
    local ok, n = pcall(function() return #ISTimedActionQueue.getTimedActionQueue(p).queue end)
    return ok and n > 0
end

-- The env re-issues a goto every step. A new target that points about the same way as the walk in progress (within ~37
-- degrees) is ignored so the path is kept and the walk does not restart every step; anything else replaces the walk.
function commands.goto(p, a)
    local x, y = tonumber(a.a), tonumber(a.b)
    local dx, dy = x - p:getX(), y - p:getY()
    local len = math.sqrt(dx * dx + dy * dy)
    local g = RL.goal
    if g and len > 0.01 and walking(p) then
        local gx, gy = g.x - p:getX(), g.y - p:getY()
        local glen = math.sqrt(gx * gx + gy * gy)
        if glen > 0.5 and (dx * gx + dy * gy) / (len * glen) > 0.8 then return true, "continue" end
    end
    local sq = getCell():getGridSquare(math.floor(x), math.floor(y), p:getZ())
    if not sq then return false, "square not loaded" end
    RL.run = true
    RL.goal = { x = x, y = y }
    ISTimedActionQueue.clear(p)
    ISTimedActionQueue.add(ISWalkToTimedAction:new(p, sq))
    return true
end
function commands.stop(p)
    ISTimedActionQueue.clear(p)
    RL.goal = nil
    RL.run = false
    return true
end
function commands.equip(p, a) return equip(p, a.a) end
function commands.attack(p)
    local z, d = nearestZombie(p, 2.0)
    if not z then return false, "miss" end
    RL.swing = { zombie = z, frames = 0 }
    return true, string.format("swing %.2f", d)
end
function commands.info(p)
    log(string.format("info %.1f %.1f weapon=%s", p:getX(), p:getY(), tostring(p:getPrimaryHandItem() and p:getPrimaryHandItem():getType())))
    return true
end

Events.OnServerCommand.Add(function(module, command, args)
    if module ~= "RLBot" then return end
    local p = localPlayer(); if not p then return end
    local f = commands[command]
    if not f then log("unknown " .. tostring(command)); return end
    local ok, res, msg = pcall(f, p, args or {})
    log(command .. " -> " .. tostring(ok) .. " " .. tostring(res) .. " " .. tostring(msg))
end)

-- swing: face the zombie, raise the weapon, point the cursor at the zombie (a local player's aim vector comes from the mouse,
-- without this the server sees attackType "miss" and almost no damage) and retry pressedAttack every frame until a swing
-- starts (presses are ignored during a hit reaction); done when that swing has finished
RL.tick = function(p)
    if RL.run then p:setRunning(true) end
    local sw = RL.swing
    if not sw then return end
    sw.frames = sw.frames + 1
    local z = sw.zombie
    if z:isDead() or sw.frames > 90 then RL.swing = nil; p:setIsAiming(false); return end
    p:faceThisObject(z); p:setIsAiming(true)
    local okc, sx, sy = pcall(ISCoordConversion.ToScreen, z:getX(), z:getY(), z:getZ(), 0)
    if okc and sx then Mouse.setXY(sx, sy) end
    if p:isAttackStarted() then sw.began = true
    elseif sw.began then RL.swing = nil; p:setIsAiming(false)
    elseif sw.frames >= 3 then p:pressedAttack() end
end
Events.OnTick.Add(function()
    local p = localPlayer(); if not p then return end
    RL.tick(p)
end)
log("RLBot loaded")
