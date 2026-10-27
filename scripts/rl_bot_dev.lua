local RL, commands, log = ...
-- tidy: keep one item of the given type in the client's own inventory (the server cannot clean a real client's inventory)
commands.tidy = function(p, a)
    local short = string.gsub((a and a.a) or "Base.BaseballBat", "^Base%.", "")
    local inv = p:getInventory()
    local all = inv:getAllTypeRecurse(short)
    for i = all:size() - 1, 1, -1 do
        local it = all:get(i); local c = it:getContainer()
        if c then c:Remove(it); pcall(sendRemoveItemFromContainer, c, it) end
    end
    return true, "tidied"
end

-- instrumentation: one COMBAT line per finished swing with the character state at the start of the swing and the zombie health lost
local function stat(p, name)
    local ok, v = pcall(function() return p:getStats():get(CharacterStat[name]) end)
    return ok and v or -1
end
local function arms(p)
    local worst = 0
    for _, part in ipairs({ "Hand_R", "ForeArm_R", "UpperArm_R", "Hand_L", "ForeArm_L", "UpperArm_L" }) do
        local ok, v = pcall(function() return p:getBodyDamage():getBodyPart(BodyPartType[part]):getStiffness() end)
        if ok and v and v > worst then worst = v end
    end
    return worst
end
local function snap(p, z)
    return string.format("zid=%d endurance=%.2f panic=%.1f stress=%.2f fatigue=%.2f pain=%.1f stiff=%.1f str=%d blunt=%d fit=%d zhp=%.3f",
        z:getOnlineID(), stat(p, "ENDURANCE"), stat(p, "PANIC"), stat(p, "STRESS"), stat(p, "FATIGUE"), stat(p, "PAIN"), arms(p),
        p:getPerkLevel(Perks.Strength), p:getPerkLevel(Perks.Blunt), p:getPerkLevel(Perks.Fitness), z:getHealth())
end
RL.autoRearm = true
RL.tick = function(p)
    if RL.run then p:setRunning(true) end
    RL.frameCount = (RL.frameCount or 0) + 1
    -- a knockdown or a broken weapon can leave the hands empty: pick the bat up again, like a player would
    if RL.autoRearm and RL.frameCount % 30 == 0 and (not p:getPrimaryHandItem() or (p:getSecondaryHandItem() ~= p:getPrimaryHandItem() and p:getPrimaryHandItem():isTwoHandWeapon())) then
        local ok = commands.equip and commands.equip(p, { a = "Base.BaseballBat" })
        log("REARM hands were empty, equip=" .. tostring(ok))
    end
    local sw = RL.swing
    if not sw then return end
    sw.frames = sw.frames + 1
    local z = sw.zombie
    if z:isDead() or sw.frames > 90 then
        if sw.began then log("COMBAT end(dead=" .. tostring(z:isDead()) .. ") " .. snap(p, z) .. " zhp_start=" .. string.format("%.3f", sw.zhp0)) end
        RL.swing = nil; p:setIsAiming(false); return
    end
    p:faceThisObject(z); p:setIsAiming(true)
    local okc, sx, sy = pcall(ISCoordConversion.ToScreen, z:getX(), z:getY(), z:getZ(), 0)
    if okc and sx and rlAim then local zm = getCore():getZoom(0); rlAim(math.floor(sx / zm), math.floor(sy / zm)) end
    if p:isAttackStarted() then
        if not sw.began then sw.began = true; sw.zhp0 = z:getHealth(); sw.s0 = snap(p, z); sw.d0 = math.sqrt((z:getX()-p:getX())^2 + (z:getY()-p:getY())^2) end
    elseif sw.began then
        log(string.format("COMBAT swing %s dmg=%.3f dist=%.2f frames=%d", sw.s0, sw.zhp0 - z:getHealth(), sw.d0, sw.frames))
        RL.swing = nil; p:setIsAiming(false); if rlAimClear then rlAimClear() end
    elseif sw.frames >= 3 then p:pressedAttack() end
end

-- aimtest: which screen conversion puts the mouse cursor on the nearest zombie? Set the cursor from each candidate, read the world
-- position under the cursor back with the game's own inverse, and log the error in tiles.
commands.aimtest = function(p)
    local list = getCell():getZombieList()
    local z, bd
    for i = 0, list:size() - 1 do
        local c = list:get(i)
        local d = math.sqrt((c:getX() - p:getX()) ^ 2 + (c:getY() - p:getY()) ^ 2)
        if not bd or d < bd then z, bd = c, d end
    end
    if not z then log("aimtest: no zombie"); return false, "none" end
    local zoom = getCore():getZoom(0)
    local function try(name, sx, sy)
        Mouse.setXY(sx, sy)
        local wx, wy = ISCoordConversion.ToWorld(Mouse.getX(), Mouse.getY(), z:getZ())
        log(string.format("aimtest %-26s cursor=(%d,%d) world_under_cursor=(%.1f,%.1f) zombie=(%.1f,%.1f) error=%.2f tiles",
            name, Mouse.getX(), Mouse.getY(), wx, wy, z:getX(), z:getY(), math.sqrt((wx - z:getX()) ^ 2 + (wy - z:getY()) ^ 2)))
    end
    log(string.format("aimtest zoom=%.2f screen=%dx%d offscreen=%dx%d player_dist=%.2f", zoom, getCore():getScreenWidth(), getCore():getScreenHeight(),
        getCore():getOffscreenWidth(0), getCore():getOffscreenHeight(0), bd))
    local a, b = ISCoordConversion.ToScreen(z:getX(), z:getY(), z:getZ(), 0)
    try("ToScreen (current)", a, b)
    try("ToScreen / zoom", a / zoom, b / zoom)
    try("ToScreen * zoom", a * zoom, b * zoom)
    local ex, ey = IsoUtils.XToScreenExact(z:getX(), z:getY(), z:getZ(), 0), IsoUtils.YToScreenExact(z:getX(), z:getY(), z:getZ(), 0)
    try("XToScreenExact", ex, ey)
    try("XToScreenExact - offset", ex - getCameraOffX(), ey - getCameraOffY())
    return true, "logged"
end

-- aimtest2: same idea, but read the cursor back a few frames AFTER setting it (the game applies Mouse.setXY on a later frame)
RL.aim = RL.aim or { q = {}, hooked = false }
commands.aimtest2 = function(p)
    local list = getCell():getZombieList()
    local z, bd
    for i = 0, list:size() - 1 do
        local c = list:get(i)
        local d = math.sqrt((c:getX() - p:getX()) ^ 2 + (c:getY() - p:getY()) ^ 2)
        if not bd or d < bd then z, bd = c, d end
    end
    if not z then return false, "none" end
    local a, b = ISCoordConversion.ToScreen(z:getX(), z:getY(), z:getZ(), 0)
    local ex, ey = IsoUtils.XToScreenExact(z:getX(), z:getY(), z:getZ(), 0), IsoUtils.YToScreenExact(z:getX(), z:getY(), z:getZ(), 0)
    local cands = { { "ToScreen", a, b }, { "XToScreenExact", ex, ey }, { "ToScreen+title(32)", a, b + 32 } }
    RL.aim.q = {}
    for _, c in ipairs(cands) do RL.aim.q[#RL.aim.q + 1] = { name = c[1], x = c[2], y = c[3], z = z, wait = 0, set = false } end
    if not RL.aim.hooked then
        RL.aim.hooked = true
        Events.OnTick.Add(function()
            local it = RL.aim.q[1]
            if not it then return end
            if not it.set then Mouse.setXY(it.x, it.y); it.set = true; it.wait = 0; return end
            it.wait = it.wait + 1
            if it.wait < 4 then return end
            local wx, wy = ISCoordConversion.ToWorld(Mouse.getX(), Mouse.getY(), it.z:getZ())
            log(string.format("aimtest2 %-20s wanted=(%d,%d) cursor_now=(%d,%d) world_under_cursor=(%.1f,%.1f) zombie=(%.1f,%.1f) error=%.2f tiles",
                it.name, it.x, it.y, Mouse.getX(), Mouse.getY(), wx, wy, it.z:getX(), it.z:getY(), math.sqrt((wx - it.z:getX()) ^ 2 + (wy - it.z:getY()) ^ 2)))
            table.remove(RL.aim.q, 1)
        end)
    end
    return true, "queued"
end


-- aimcheck: angle between the game's aim vector for this player and the direction to the nearest zombie, with the override off and on
commands.aimcheck = function(p)
    local list = getCell():getZombieList()
    local z, bd
    for i = 0, list:size() - 1 do
        local c = list:get(i)
        local d = math.sqrt((c:getX() - p:getX()) ^ 2 + (c:getY() - p:getY()) ^ 2)
        if not bd or d < bd then z, bd = c, d end
    end
    if not z then log("aimcheck: no zombie"); return false, "none" end
    local want = math.atan2(z:getY() - p:getY(), z:getX() - p:getX())
    local function aimangle()
        local v = Vector2.new()
        p:getAimVector(v)
        return math.atan2(v:getY(), v:getX())
    end
    local function diff(a) local d = math.abs(a - want) % (2 * math.pi); if d > math.pi then d = 2 * math.pi - d end; return d * 180 / math.pi end
    if rlAimClear then rlAimClear() end
    local off = diff(aimangle())
    local zm = getCore():getZoom(0)
    local sx, sy = ISCoordConversion.ToScreen(z:getX(), z:getY(), z:getZ(), 0)
    if rlAim then rlAim(math.floor(sx / zm), math.floor(sy / zm)) end
    local on = diff(aimangle())
    if rlAimClear then rlAimClear() end
    log(string.format("aimcheck rlAim=%s zombie_dist=%.2f angle_error_without_override=%.1f deg with_override=%.1f deg", tostring(rlAim ~= nil), bd, off, on))
    return true, "logged"
end


-- equip: wield the best-condition item of the given type and restore its condition to full. A bat has 15 condition points and loses them
-- with hits; a character that fights for hours breaks it, and a broken bat leaves the hands empty (the real character's bat did break during
-- the experiments). Episodes are short, so a full-condition weapon at the start of each is the right thing to simulate.
commands.equip = function(p, a)
    local short = string.gsub((a and a.a) or "Base.BaseballBat", "^Base%.", "")
    local all = p:getInventory():getAllTypeRecurse(short)
    local best, bc = nil, -1
    for i = 0, all:size() - 1 do
        local it = all:get(i)
        local c = it:getCondition()
        if c > bc then best, bc = it, c end
    end
    if not best then log("equip: no " .. short .. " in the inventory"); return false, "none" end
    pcall(function() best:setCondition(best:getConditionMax()) end)
    -- a bat is a "two-handed" weapon (full damage only with both hands; one-handed it does half the damage for a much larger endurance cost),
    -- but isRequiresEquippedBothHands() is false for it, so ask isTwoHandWeapon() as well
    local two = false
    pcall(function() two = best:isTwoHandWeapon() end)
    if not two then pcall(function() two = best:isRequiresEquippedBothHands() end) end
    p:setPrimaryHandItem(best)
    if two then p:setSecondaryHandItem(best) end
    log(string.format("equip %s condition %d -> %d/%d two_handed=%s both_hands_holding=%s", short, bc, best:getCondition(), best:getConditionMax(), tostring(two),
        tostring(p:getSecondaryHandItem() == best)))
    return true, "ok"
end
