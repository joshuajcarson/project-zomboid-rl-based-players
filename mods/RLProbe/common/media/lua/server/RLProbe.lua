-- Research probe for option B (server-side NPC players). Prints "RLPROBE" lines to the server log.
local NPC_X, NPC_Y, NPC_Z = 10650, 9800, 0
local SPAWN_AT_TICK, REPORT_EVERY = 600, 150
local ticks, npc, prevZ = 0, nil, {}

local function log(msg) print("RLPROBE " .. tostring(msg)) end

local function spawnNpc()
    local cell = getCell()
    local sq = cell and cell:getGridSquare(NPC_X, NPC_Y, NPC_Z)
    log("pre-spawn square loaded=" .. tostring(sq ~= nil))
    local ok, res = pcall(function()
        local desc = SurvivorFactory.CreateSurvivor()
        local p = IsoPlayer.new(cell, desc, NPC_X, NPC_Y, NPC_Z)
        return p
    end)
    if not ok then log("IsoPlayer.new failed: " .. tostring(res)); return end
    npc = res
    log("IsoPlayer.new ok: " .. tostring(npc))
    local ok2, err2 = pcall(function() npc:setNpc(true) end)
    log("setNpc ok=" .. tostring(ok2) .. " " .. tostring(err2 or ""))
    pcall(function() npc:setSceneCulled(false) end)
end

local function report()
    local cell = getCell()
    local players = getOnlinePlayers()
    local zl = cell and cell:getZombieList()
    local nz = zl and zl:size() or -1
    local line = "tick=" .. ticks .. " onlinePlayers=" .. (players and players:size() or -1) .. " zombiesInCell=" .. nz
    if npc then
        local sq = cell:getGridSquare(npc:getX(), npc:getY(), npc:getZ())
        line = line .. " npc=(" .. math.floor(npc:getX()) .. "," .. math.floor(npc:getY()) .. ") npcSquareLoaded=" .. tostring(sq ~= nil)
            .. " npcOnlineId=" .. tostring(npc:getOnlineID())
    end
    -- are zombies moving? compare positions of the first few against last report
    local moved, cur = 0, {}
    for i = 0, math.min(nz, 40) - 1 do
        local z = zl:get(i)
        local id = z:getOnlineID()
        cur[id] = { z:getX(), z:getY() }
        if prevZ[id] and (math.abs(prevZ[id][1] - cur[id][1]) + math.abs(prevZ[id][2] - cur[id][2])) > 0.05 then moved = moved + 1 end
    end
    prevZ = cur
    -- optional live expressions: put one rlGet expression per line in <cache>/Lua/rlprobe_exprs.txt
    if rlGet then
        local okr, rd = pcall(getFileReader, "rlprobe_exprs.txt", false)
        if okr and rd then
            local ln = rd:readLine()
            while ln do
                if ln ~= "" then log("EXPR " .. ln .. " = " .. tostring(rlGet(ln))) end
                ln = rd:readLine()
            end
            rd:close()
        end
    end
    log(line .. " zombiesMovedSinceLast=" .. moved)
end

Events.OnTick.Add(function()
    ticks = ticks + 1
    -- rlLoadArea is installed by the Java agent (agent/rl-agent.jar); keeps the NPC's area loaded
    if npc and rlLoadArea and true then
        local ok, res = pcall(rlLoadArea, math.floor(npc:getX()), math.floor(npc:getY()), math.floor(npc:getZ()))
        if ticks % REPORT_EVERY == 0 then log("rlLoadArea -> " .. tostring(ok) .. " " .. tostring(res)) end
    end
    if ticks == SPAWN_AT_TICK then spawnNpc() end
    if ticks % REPORT_EVERY == 0 then local ok, e = pcall(report); if not ok then log("report error " .. tostring(e)) end end
end)
log("RLProbe loaded")
