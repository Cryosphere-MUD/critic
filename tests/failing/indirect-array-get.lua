local count = getint(get("level1_1"), "dock.count")

for i=0,count-1 do
        local prop = "dock." .. i
        local o = getobj("level1_1", prop)
        local other = getobj(o, "notexist")
        other:send("hello")
end