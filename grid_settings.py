the_settings = {
    "grid_width": 4,
    "grid_height": 3,
    "start_location": (0,2),
    "reward_locations": {
        (3,0): 1,
        (3,1): -1
    },
    "blocked_locations": [(1,1)],
    "terminating_locations": [(3,0), (3,1)],
    "probablistic_action_adjuster": {
        "correct": 0.8,
        "slide_left": 0.1,
        "slide_right": 0.1
    },
    "alpha": 0.1,
    "gamma": 0.9,
    "epsilon": 0.7,
    "auto": True,
    "iterations": 60,
    "sleep_between_moves": 0.0,
    "print_logs": True,
    "default_direction": "R"
}
