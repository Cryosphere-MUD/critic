

local farcomp = (aowner and aowner ~= powner and owner(aowner) ~= powner) or
                  (bowner and bowner ~= powner and owner(bowner) ~= powner)
