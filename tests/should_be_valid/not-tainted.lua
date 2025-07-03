local bzone = nil
local dock = nil

for i=0,o1.docks.count-1 do
  local dzone = o1.docks[i].bzone
  if dzone == o3.zone then
    dock = o1.docks[i].dock
    bzone = o3.zone
  end
end

local fakedests = { "Landfall", "Kingston", "Churchill", "Cenotaph", "Epsilon Eridani", "Tau Ceti", "New New York", "Barnard's Star", "Luyten's Star", "van Maanen's Star", "Sirius", "Epona", "Mountbatten", "Beta Hydri", "Zeta Tucanae", "Wolf 354", "Ross 154", "Lave", "Swan" }

local a = dock
local b = fakedests[random(#fakedests) + 1]

local t = a .. b

print(a)
print(b)
print(t)

local ship = make.clone_ship("mini_smallcargo_1", o2)
set(ship, "plan", t)

