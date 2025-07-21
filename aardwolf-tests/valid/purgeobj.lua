--- Purge all tickets carried by self.
purgeobj("all.ticket",LP_CARRIEDONLY)

--- Purge all instances of aylor-321 in room, visible or not.
purgeobj("aylor-321",LP_ROOMONLY+LP_SEEALL)

--- Purge the item that triggered this prog (give trigger)
purgeobj(obj)
