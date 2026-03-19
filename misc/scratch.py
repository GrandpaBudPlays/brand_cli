import os
import random
from file_manager import read_file

def _build_markdown(original_data: dict, final_data: dict, session) -> str:
    md = ""
    
    # Append World Seed section
    try:
        world_seed_path = os.path.join(
            os.path.dirname(os.path.dirname(session.path)), 
            "World Seed.md"
        )
        world_seed_content = read_file(world_seed_path)
        if world_seed_content:
            invitations = [line for line in world_seed_content.split('\n') 
                         if line.startswith(tuple(str(i) for i in range(1,10)))]
            if invitations:
                selected_invitation = random.choice(invitations)
                md += "\n---\n\n"
                md += "## 🌱 World Seed\n\n"
                md += f"**Seed:** L4y2XbwA0V (Valheim 0.217.46)\n\n"
                md += f"**Elder's Invitation:**\n{selected_invitation}\n\n"
                md += "*To play along on this same world, use the seed above.*"
    except Exception as e:
        print(f"Warning: Could not append World Seed - {str(e)}")
    
    return md