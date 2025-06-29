local o1
local n, x, o, y

  n = 0
  x = 1

  n = getintd(o1, "!timelimit", 300)

  if n>0 then
    set(o1, "!plan.!wait", n.." file_plan stuff")
    obj.interpret(o1, "file_plan !wait")
  end
