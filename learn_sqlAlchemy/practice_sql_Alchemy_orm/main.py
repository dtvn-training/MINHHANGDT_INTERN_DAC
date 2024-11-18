from logics.database import init_db
from logics.database import SessionLocal
from logics.interact_with_db import add_actor, get_all_actors

def main():
    try:
        session = SessionLocal()
        add_actor(session,"Shika", "Shika Yuha", 2)
        add_actor(session,"Conan", "Conan Dio", 2)
        actors = get_all_actors(session)

        for actor in actors:
            print(actor.id, actor.name, actor.fullname)

    except Exception as e:
        print(f"An error occurred: {e}")  # Log the error message

if __name__ == "__main__":
    try:
        init_db()
    except Exception as e:
        print(f"An error occurred: {e}")
    main()
    