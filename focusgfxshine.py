import re

def get_shine_def(name, path):
    return """
    SpriteType = {
        name = "%s_shine"
        texturefile = "%s"
        effectFile = "gfx/FX/buttonstate.lua"
        animation = {
            animationmaskfile = "%s"
            animationtexturefile = "gfx/interface/goals/shine_overlay.dds"
            animationrotation = -90.0
            animationlooping = no
            animationtime = 0.75
            animationdelay = 0
            animationblendmode = "add"
            animationtype = "scrolling"
            animationrotationoffset = { x = 0.0 y = 0.0 }
            animationtexturescale = { x = 1.0 y = 1.0 }
        }

        animation = {
            animationmaskfile = "%s"
            animationtexturefile = "gfx/interface/goals/shine_overlay.dds"
            animationrotation = 90.0
            animationlooping = no
            animationtime = 0.75
            animationdelay = 0
            animationblendmode = "add"
            animationtype = "scrolling"
            animationrotationoffset = { x = 0.0 y = 0.0 }
            animationtexturescale = { x = 1.0 y = 1.0 }
        }
        legacy_lazy_load = no
    }""" % (
        name,
        path,
        path,
        path,
    )

def process_goals_files(goals_path, goals_shine_path):
    goal_regex = re.compile(
        r"name\s*=\s*\"([^\"]+)?\"(?:[^\}]*?)texturefile\s*=\s*\"([^\"]+)?\"",  re.MULTILINE | re.DOTALL | re.IGNORECASE
    )
    goal_name_regex = re.compile(
        r"name\s*=\s*\"([^\"]+)?\"",  re.MULTILINE | re.DOTALL | re.IGNORECASE
    )
    comments_regex = re.compile(
        r"#*$"
    )

    with open(goals_shine_path, "r") as f:
        goals_shine = f.read()

    goals_shine_matches = goal_name_regex.findall(
        comments_regex.sub(goals_shine, '')
    )
    goals_shine_matches = set(goals_shine_matches)

    last_bracket_idx = 0

    for i in range(len(goals_shine) - 1, -1, -1):
        if goals_shine[i] == "}":
            last_bracket_idx = abs(i)
            break

    goals_shine_split = [goals_shine[:last_bracket_idx], goals_shine[last_bracket_idx:]]

    with open(goals_path, "r") as f:
        goals = f.read()

    goals_matches = goal_regex.findall(
        comments_regex.sub(goals, '')
    )
    goals_matches = {
        k: v for k, v in goals_matches if not f"{k}_shine" in goals_shine_matches
    }

    for k, v in goals_matches.items():
        goals_shine_split.insert(1, get_shine_def(k, v))

    with open(goals_shine_path, "w") as f:
        f.write("\n".join(goals_shine_split))

# Example usage

