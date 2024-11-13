from logics.models.actor import Actor

def add_actor(session, name, fullname, body_count):
    new_actor = Actor(name = name, fullname = fullname, body_count=body_count)
    session.add(new_actor)
    session.commit()

def get_all_actors(session):
    return session.query(Actor).all()
