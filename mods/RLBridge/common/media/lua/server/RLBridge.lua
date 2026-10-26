-- Server-side bridge for the Python RL environment. Research only.
--  * every OBS_EVERY server ticks, publishes one JSON line with all online players (and the zombies near each) via rlPublish
--  * every tick, drains commands received through rlPoll ("name|arg|arg", see handlers below)
-- rlPublish / rlPoll are registered by agent/rl-agent.jar (-ChannelPort); without it this mod only logs.
-- biteDamage: hit points removed per adjacent zombie per game second (0 = off). The fake client's zombie model does
-- essentially no damage to players, so this is how the environment makes zombies dangerous.
-- minHp: the synthetic bite never takes a player below this health, so a training episode that goes badly ends at the env's death
-- threshold without the character truly dying (a dead character cannot be healed: it would have to be recreated, which costs minutes)
local cfg = { obsEvery = 5, zRadius = 30, zMax = 8, biteDamage = 0, biteRange = 1.2, minHp = 3 }
local ticks = 0
local biteScale = {}   -- per player multiplier on the synthetic bite (a landed hit staggers the zombies: the env lowers it for a few seconds)
local failed = {}

local function log(msg) print("RLBRIDGE " .. msg) end

local function try(name, f, default)
    local ok, v = pcall(f)
    if ok and v ~= nil then return v end
    if not failed[name] then failed[name] = true; log("failed: " .. name .. " (" .. tostring(v) .. ")") end
    return default
end

local function jstr(s) return '"' .. tostring(s):gsub('[%c"\\]', '') .. '"' end
local function num(v, fmt) return string.format(fmt or "%.2f", tonumber(v) or 0) end

local function stat(p, name)
    return try("stat." .. name, function() return p:getStats():get(CharacterStat[name]) end, 0)
end

local function playerJson(p, zl)
    local px, py = p:getX(), p:getY()
    local r2 = cfg.zRadius * cfg.zRadius
    local near = {}
    for i = 0, zl:size() - 1 do
        local z = zl:get(i)
        local dx, dy = z:getX() - px, z:getY() - py
        local d2 = dx * dx + dy * dy
        if d2 <= r2 then near[#near + 1] = { d2, z:getX(), z:getY() } end
    end
    table.sort(near, function(a, b) return a[1] < b[1] end)
    local zs = {}
    for i = 1, math.min(#near, cfg.zMax) do zs[i] = "[" .. num(near[i][2], "%.1f") .. "," .. num(near[i][3], "%.1f") .. "]" end
    local weapon = try("weapon", function() local it = p:getPrimaryHandItem(); return it and it:getFullType() or "" end, "")
    local bag = try("bag", function() return p:getClothingItem_Back() ~= nil end, false)
    return string.format(
        '{"u":%s,"x":%.2f,"y":%.2f,"z":%d,"hp":%.1f,"dead":%s,"hunger":%.3f,"thirst":%.3f,"fatigue":%.3f,"items":%d,"kills":%d,"weapon":%s,"bag":%s,"zn":%d,"z":[%s]}',
        jstr(try("username", function() return p:getUsername() end, "?")), px, py, p:getZ(),
        try("health", function() return p:getBodyDamage():getHealth() end, 0),
        tostring(try("dead", function() return p:isDead() end, false)),
        stat(p, "HUNGER"), stat(p, "THIRST"), stat(p, "FATIGUE"),
        try("items", function() return p:getInventory():getItems():size() end, 0),
        try("kills", function() return p:getZombieKills() end, 0),
        jstr(weapon), tostring(bag), #near, table.concat(zs, ","))
end

-- reduce a player's health; tries the Build 42 body damage API variants
local function hurt(p, amount)
    local bd = p:getBodyDamage()
    local ok = pcall(function() bd:ReduceGeneralHealth(amount) end)
    if ok then return true end
    return pcall(function() bd:setOverallBodyHealth(bd:getOverallBodyHealth() - amount) end)
end

local function applyBites(players, zl)
    if cfg.biteDamage <= 0 then return end
    local r2 = cfg.biteRange * cfg.biteRange
    local dt = cfg.obsEvery / 10   -- one publish = obsEvery ticks = obsEvery/10 game seconds
    for i = 0, players:size() - 1 do
        local p = players:get(i)
        local near = 0
        for j = 0, zl:size() - 1 do
            local z = zl:get(j)
            local dx, dy = z:getX() - p:getX(), z:getY() - p:getY()
            if dx * dx + dy * dy <= r2 then near = near + 1 end
        end
        if near > 0 then
            local health = try("health", function() return p:getBodyDamage():getHealth() end, 100)
            local user = try("username", function() return p:getUsername() end, "")
            local amount = math.min(near * cfg.biteDamage * (biteScale[user] or 1.0) * dt, math.max(0, health - cfg.minHp))
            local ok = amount <= 0 or hurt(p, amount)
            if not ok and not failed["hurt"] then failed["hurt"] = true; log("failed: hurt") end
        end
    end
end

local function publishObs()
    local players = getOnlinePlayers()
    if not players then return end
    local zl = getCell():getZombieList()
    applyBites(players, zl)
    local parts = {}
    for i = 0, players:size() - 1 do
        local ok, res = pcall(playerJson, players:get(i), zl)
        if ok then parts[#parts + 1] = res else log("obs error " .. tostring(res)) end
    end
    local age = try("ageH", function() return getGameTime():getWorldAgeHours() end, 0)
    local line = string.format('{"tick":%d,"ageH":%.4f,"nz":%d,"p":[%s]}', ticks, age, zl:size(), table.concat(parts, ","))
    if rlPublish then rlPublish(line) end
end

local function findPlayer(user)
    local players = getOnlinePlayers()
    for i = 0, players:size() - 1 do
        local p = players:get(i)
        if try("username", function() return p:getUsername() end, "") == user then return p end
    end
end

local function ack(cmd, ok, msg)
    if rlPublish then rlPublish(string.format('{"ack":%s,"ok":%s,"msg":%s}', jstr(cmd), tostring(ok), jstr(msg or ""))) end
end

-- command handlers: handlers[name](args...) returns ok, message
local handlers = {}

function handlers.cfg(key, value)
    if cfg[key] == nil then return false, "unknown key" end
    cfg[key] = tonumber(value) or cfg[key]
    return true, key .. "=" .. tostring(cfg[key])
end

function handlers.heal(user)
    local p = findPlayer(user); if not p then return false, "no such player" end
    local ok, err = pcall(function()
        p:getBodyDamage():RestoreToFullHealth()
        for _, name in ipairs({ "HUNGER", "THIRST", "FATIGUE" }) do
            pcall(function() p:getStats():set(CharacterStat[name], 0) end)
        end
    end)
    return ok, tostring(err or "healed")
end

-- give|user|Base.Item : the ack message is the new item's id (the fake client needs it to wield a weapon)
function handlers.give(user, itemType)
    local p = findPlayer(user); if not p then return false, "no such player" end
    local ok, res = pcall(function() return p:getInventory():AddItem(itemType) end)
    if ok and res ~= nil then
        local okId, id = pcall(function() return res:getID() end)
        return true, "id=" .. tostring(okId and id or "?")
    end
    return false, tostring(res)
end

-- bitescale|user|f : multiply that player's synthetic bite damage by f (1 = normal)
function handlers.bitescale(user, f)
    biteScale[user] = tonumber(f) or 1.0
    return true, "ok"
end

-- ensure|user|Base.Item : make sure the player owns exactly one of this item type (the starter kit already puts a bat in the
-- backpack, as in the real game): keeps the first one found anywhere in the inventory, removes extras, adds one only if
-- there is none. The ack message is "id=N count_before=M", N is the kept item's id (a fake client needs it to wield it).
function handlers.ensure(user, itemType)
    local p = findPlayer(user); if not p then return false, "no such player" end
    local short = string.gsub(itemType, "^Base%.", "")
    local ok, res = pcall(function()
        local inv = p:getInventory()
        local all = inv:getAllTypeRecurse(short)
        local before = all:size()
        local keep = before > 0 and all:get(0) or inv:AddItem(itemType)
        for i = 1, before - 1 do
            local extra = all:get(i)
            local c = extra:getContainer()
            if c then c:Remove(extra) end
        end
        return "id=" .. tostring(keep:getID()) .. " count_before=" .. tostring(before)
    end)
    return ok, tostring(res)
end

-- inv|user : what the player carries (a heavy load slows walking): item count, carried weight, and bats
function handlers.inv(user)
    local p = findPlayer(user); if not p then return false, "no such player" end
    local ok, res = pcall(function()
        local inv = p:getInventory()
        return string.format("items=%d weight=%.1f bats=%d", inv:getItems():size(), inv:getCapacityWeight(), inv:getAllTypeRecurse("BaseballBat"):size())
    end)
    return ok, tostring(res)
end

-- admin|user : give a fake client the admin role so the server accepts its teleports and chat commands
function handlers.admin(user)
    if not rlPromote then return false, "agent function rlPromote missing" end
    local res = rlPromote(user)
    return string.sub(res, 1, 8) == "promoted", res
end

-- tp|user|x|y|z : server-side teleport; tries several APIs and reports which one worked
function handlers.tp(user, x, y, z)
    local p = findPlayer(user); if not p then return false, "no such player" end
    x, y, z = tonumber(x), tonumber(y), tonumber(z) or 0
    local ok1, e1 = pcall(function() p:teleportTo(x, y, z) end)
    if ok1 then return true, "teleportTo" end
    local ok2, e2 = pcall(function() p:setX(x); p:setY(y); p:setZ(z); p:setLastX(x); p:setLastY(y) end)
    return ok2, "teleportTo failed (" .. tostring(e1) .. "); setX/Y " .. tostring(ok2 and "ok" or e2)
end

-- bot|user|cmd|a|b : forward an action to that rendered client's RLBot.lua (goto x y, stop, equip Base.Item, attack, info)
function handlers.bot(user, cmd, a, b)
    local p = findPlayer(user); if not p then return false, "no such player" end
    sendServerCommand(p, "RLBot", cmd, { a = a, b = b })
    return true, "sent"
end

-- spawn n zombies around (x, y): zspawn|x|y|n
function handlers.zspawn(x, y, n)
    local ok, res = pcall(function() return addZombiesInOutfit(tonumber(x), tonumber(y), 0, tonumber(n), nil, 50) end)
    return ok, tostring(res)
end

-- remove every zombie within r of (x, y): zclear|x|y|r
function handlers.zclear(x, y, r)
    x, y, r = tonumber(x), tonumber(y), tonumber(r)
    local zl, removed, errs = getCell():getZombieList(), 0, ""
    local victims = {}
    for i = 0, zl:size() - 1 do
        local z = zl:get(i)
        if (z:getX() - x) ^ 2 + (z:getY() - y) ^ 2 <= r * r then victims[#victims + 1] = z end
    end
    for _, z in ipairs(victims) do
        local ok, err = pcall(function() z:removeFromWorld(); z:removeFromSquare() end)
        if ok then removed = removed + 1 else errs = tostring(err) end
    end
    return true, "removed " .. removed .. " " .. errs
end

-- development-only commands, present only when the server was started with -Dev (rl.dev=true)
if rlDev then
    -- get|<reflection path>  : see agent rlGet, e.g. get|zombie.network.GameServer.Players.size()
    function handlers.get(expr) return true, tostring(rlGet(expr)) end
    -- lua|<code> : run a chunk of Lua on the server and return its result
    function handlers.lua(code)
        local f, err = loadstring("return " .. code)
        if not f then f, err = loadstring(code) end
        if not f then return false, tostring(err) end
        local ok, res = pcall(f)
        return ok, tostring(res)
    end
end

local function drain()
    for _ = 1, 50 do
        local line = rlPoll and rlPoll()
        if not line then return end
        local parts = {}
        for piece in string.gmatch(line, "[^|]+") do parts[#parts + 1] = piece end
        local h = handlers[parts[1] or ""]
        if h then
            local args = { unpack(parts, 2) }
            if parts[1] == "lua" or parts[1] == "get" then args = { string.sub(line, #parts[1] + 2) } end
            local ok, a, b = pcall(h, unpack(args))
            if ok then ack(line, a, b) else ack(line, false, tostring(a)) end
        else
            ack(line, false, "unknown command")
        end
    end
end

Events.OnTick.Add(function()
    ticks = ticks + 1
    drain()
    if ticks % cfg.obsEvery == 0 then
        local ok, err = pcall(publishObs)
        if not ok then log("publish error " .. tostring(err)) end
    end
end)
log("RLBridge loaded (channel " .. tostring(rlPublish ~= nil) .. ")")
