


#TODO? moet door Stelain een ok krijgen nadat server.py gerefactored is (versie 1.0 klaar is)

# POST
# TODO: create parking lot (admin only)             /parking-lots
# TODO: start parking session by lid                /parking-lots/{lid}/sessions/start
# TODO: end parking session by lid                  /parking-lots/{lid}/sessions/stop

# GET
# TODO: get all parking lots                        /parking-lots/
# TODO: get parking lot by lid                      /parking-lots/{lid}
# TODO: get all sessions lot by lid (admin only)    /parking-lots/{lid}/sessions
# TODO: get session by session sid (admin only)     /parking-lots/{lid}/sessions/{sid}

# TODO?: get parking lots availability               /parking-lots/availability
# TODO?: get parking lot availability by id          /parking-lots/{id}/availability
# TODO?: search parking lots                         /parking-lots/search
# TODO?: get parking lots by city                    /parking-lots/city/{city}
# TODO?: get parking lots by location                /parking-lots/location/{location}
# TODO?: get parking lot reservations                /parking-lots/{id}/reservations
# TODO?: get parking lot stats (admin only)          /parking-lots/{id}/stats

# PUT
# TODO: update parking lot by lid (admin only)      /parking-lots/{lid}

# DELETE
# TODO: delete parking lot by lid (admin only)      /parking-lots/{lid}
# TODO: delete session by session lid (admin only)  /parking-lots/{lid}/sessions/{sid}