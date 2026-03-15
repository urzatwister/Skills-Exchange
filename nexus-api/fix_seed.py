import os

with open("seed.py", "r", encoding="utf-8") as f:
    content = f.read()

# Find the start of the first generated skill
idx = content.find('    {\n        "skill_id": "agent-skill-')

if idx != -1:
    new_content = content[:idx] + """]

def seed(generated_skills=None):
    from generate_skills import generate_100_skills
    from db import init_db, insert_skill

    if generated_skills is None:
        generated_skills = generate_100_skills()

    all_skills = SAMPLE_SKILLS + generated_skills

    print("Initializing database...")
    init_db()
    
    print(f"Seeding {len(all_skills)} skills...")
    for skill in all_skills:
        insert_skill(skill)
        print(f"  + {skill['name']} ({skill['skill_id']})")
    print("Done!")

if __name__ == "__main__":
    seed()
"""
    with open("seed.py", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Successfully patched seed.py.")
else:
    print("Could not find generated skills in seed.py")
