"""
This is the 'service-like' API to the experiments app.  It may at some point be
exposed via http views, but for now is just an in-process interface.
"""

class Condition(object):
    """
    Note: these should be stored with the course (so in Mongo today)
    """
    def __init__(self):
        self.id
        self.name

    def to_json(self):
        pass


class Experiment(object):
    """
    Note: these should be stored with the course (so in Mongo today)
    """
    def __init__(self):
        self.id
        self.name
        self.description
        self.conditions = list(Condition)

    def to_json(self):
        pass

    
def get_condition_for_user(course_id, experiment_id, user_id):
    """
    If the user is already assigned to a condition for experiment_id, return the
    condition_id.

    If not, assign them to one of the conditions, persist that decision, and
    return the condition_id.

    If the condition they are assigned to doesn't exist anymore, re-assign to one of
    the existing conditions and return its id.
    """
    return 1
