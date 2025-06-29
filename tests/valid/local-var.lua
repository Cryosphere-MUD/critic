local argc, arg, obj, pl

if argc < 1 then
  send(pl,"Usage: spellcheck <object> [property]")
  send(pl,"       spellcheck zone <zone>")
  send(pl,"       spellcheck word <word>")
  send(pl,"       spellcheck phrase <word> [word...]")
  send(pl,"       spellcheck all")
  return
end

local obj = {}

if arg[1] == "word" then
  if argc ~= 2 then
    send(pl,"Usage: spellcheck word <word>")
    return
  end

  local w = util.toascii(table.concat(arg, " ", 2))
  local suggestions = util.check_spelling(w)

  if #suggestions > 0 then
    pl:send("Suggested spellings:")
    pl:send("  ^Z" .. table.concat(suggestions,", "))
  else
    pl:send("\"" .. w .. "\" seems fine.")
  end

  return
elseif arg[1] == "phrase" then
  if argc < 2 then
    send(pl,"Usage: spellcheck phrase <word> [word...]")
    return
  end

  table.remove(arg, 1)
  table.remove(arg, 1)

  local typos = 0

  for i,v in ipairs(arg) do
    local w = util.toascii(v)
    local suggestions = util.check_spelling(w)
    if #suggestions > 0 then
      typos = typos + 1
      pl:send("^r" ..w.. "^n:")
      pl:send("  ^Z^W" .. table.concat(suggestions,"^n, ^W") .. "^n")
    end
  end

  if typos == 0 then
    pl:send("\"" .. arg .. "\" seems fine.")
  end

    return
elseif arg[1] == "zone" then
  if argc ~= 2 then
    send(pl,"Usage: spellcheck zone <zone>")
    return
  end

  obj = zone(arg[2])

  if not obj or #obj < 1 then
    send(pl,"Can't find anything in zone ^`^W"..arg[2].."^n^'.")
    return
  end
elseif arg[1] == "all" then
  local zones = children("@musicmud")
  local ztab = {}

  for i,v in ipairs(zones) do
    local zonestr = getstr(v,"zone")
    if zonestr and not ztab[zonestr] then
      ztab[zonestr ] = 1
      for j,w in ipairs(zone(zonestr)) do
        table.insert(obj,w)
      end
    end
  end
elseif arg[1] == "public" then
  local zones = children("@musicmud")
  local ztab = {}

  for i,v in ipairs(zones) do
    local ok = true

    if mud.zone_getflag(v, flag.Personal) then ok = false
      elseif mud.zone_getflag(v, flag.Private) then ok = false
      elseif v.quest and mission.find(v.quest) and quest[v.quest]:getflag(flag.Private) then ok = false
    end

    if ok then
      local zonestr = getstr(v,"zone")

      if zonestr and not ztab[zonestr ] then
        ztab[zonestr] = 1
        for j,w in ipairs(zone(zonestr)) do
          table.insert(obj,w)
        end
      end
    end
  end
elseif arg[1] == "mine" then
  local zones = children("@musicmud")
  local ztab = {}

  for i,v in ipairs(zones) do
    local ok = true

    if not v.author or not string.find(v.author, pl.id, 1, 1) then ok = false end

    if ok then
      local zonestr = getstr(v,"zone")

      if zonestr and not ztab[zonestr ] then
        ztab[zonestr] = 1
        for j,w in ipairs(zone(zonestr)) do
          table.insert(obj,w)
        end
      end
    end
  end
else
  obj = mud.match(pl,arg)

  if not obj or #obj < 1 then
    obj = {}
    local objbyid = get(arg[1])
    if objbyid then table.insert(obj,objbyid) end
  end

  if not obj or #obj < 1 then
    if arg[1] == "here" then
      table.insert(obj, pl:owner())
    end
  end

  if not obj or #obj < 1 then
    send(pl,"Can't find object ^`^W"..arg[1].."^n^'.")
    return
  end
end

obj = util.filter_out_temporary(obj)

local checked = 0
local passed = 0

local routine = function()
  for i,v in pairs(obj) do
    if is_valid_object(v) then
      local done = 0
      local okay = 0
      local props = getprops(v,"desc.")

      for i,v in pairs(getprops(v, "short_desc")) do
        if i ~= "desc.from" then
          props[i] = v
        end
      end
      for i,v in pairs(getprops(v, "name")) do
        props[i] = v
      end
      for i,v in pairs(getprops(v, "long")) do
        props[i] = v
      end
      for i,v in pairs(getprops(v, "tell.")) do
        if v:sub(1, 4) == "tell" then
          props[i] = v
        end
      end
      for i,v in pairs(getprops(v, "rant.")) do
        if i ~= "rant.count" and i ~= "rant.speed" and type(v) == "string" and (v:sub(1, 4) == "tell" or v:sub(1, 3) == "say" or v:sub(1, 6) == "mutter" or v:sub(1, 7) == "whisper") then
          props[i] = v
        end
      end

      checked = checked + 1

      local shownid = nil

      for p,c in pairs(props) do
        if coroutine.running() and get_max_opcount() > 0 and get_opcount() > (get_max_opcount() / 1.2) then
          coroutine.yield()
        end

        done = done + 1

        local typos = {}
        c = string.gsub(c, "%^`", "")
        c = string.gsub(c, "%^'", "")
        local text = util.toascii(c)
        local words = explode(text,"(%a%w*'?%w*)")

        for i,w in ipairs(words) do
          if not tonumber(w) and w ~= w:upper() and w:sub(-1) ~= "'" then
            local suggestions = util.check_spelling(w)

            if #suggestions > 0 then table.insert(typos, w) end
          end
        end

        if #typos > 0 then
          if not shownid then
            send(pl,"Checking "..v.id)
            shownid = 1
          end

          send(pl,"  "..p.." ^Rfailed^n!")
          send(pl,"    "..table.concat(typos, ", "))
        else
          okay = okay + 1
        end
      end

      if okay == done then
        passed = passed + 1
      end
    end
  end

  send(pl,passed.." of "..checked.." objects passed spell checking")
end

if #obj > 1 then
  register_coroutine(routine)
else
  routine()
end
