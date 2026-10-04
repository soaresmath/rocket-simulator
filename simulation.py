def run_simulation(rocket):

    rocket.launch()

    while rocket.status == "LAUNCHED":
        rocket.move(1)

    return rocket