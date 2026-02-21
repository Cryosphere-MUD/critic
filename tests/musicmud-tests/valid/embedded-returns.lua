local a = nil

if math.random(2)>0 then
  if math.random(2)>0 then
    error()
  else
    return
  end
else
  a = "level2"
end

zone(a)