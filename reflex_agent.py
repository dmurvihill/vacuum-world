class ReflexAgent(object):
    def decide(self, percept):
        if "is_dirty" not in percept.keys():
            raise ValueError("Missing dirt status")
        if "agent_location" not in percept.keys():
            raise ValueError("Missing agent location")
        if type(percept["is_dirty"]) is not bool:
            raise ValueError("Illegal dirt status")
        if percept["agent_location"] not in ['A', 'B']:
            raise ValueError("Illegal agent location")
        if percept["is_dirty"]:
            decision = 'SUCK'
        elif percept["agent_location"] == 'A':
            decision = 'RIGHT'
        else:
            decision = 'LEFT'
        return decision
