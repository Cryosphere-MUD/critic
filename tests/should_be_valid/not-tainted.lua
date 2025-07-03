local fakedests = { "Landfall", "Kingston", "Churchill", "Cenotaph", "Epsilon Eridani", "Tau Ceti", "New New York", "Barnard's Star", "Luyten's Star", "van Maanen's Star", "Sirius", "Epona", "Mountbatten", "Beta Hydri", "Zeta Tucanae", "Wolf 354", "Ross 154", "Lave", "Swan" }
set(ship, "plan", "0 dockat level1_1 "..fakedests[random(#fakedests) + 1]..";0 file_plan stripe")
