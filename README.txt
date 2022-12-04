## DESCRIPTION

Our project, REP-G, is a visualization tool that aims to help United States citizens, residents, and immigrants to better understand the roles that their elected representatives play and key politicians for and against policies within Congress.

Given a political topic/subtopic, our tool displays various "clusters" (or groups of politicans) that vote together similarly on it, and details about their names, political affiliations, committee memberships, and lobbyist relations.

## INSTALLATION

If you would simply like to view our application, it is available online at: https://rep-g-app-ohzw7utbdq-uk.a.run.app/. You can install the application locally by following the instructions below.

This application uses Python. We recommend creating and using a virtual environment using the following commands in the folder where you have stored REP-G on the command line.

If you are familiar with virtual environments, you can skip to the step "Install and run the application"

### Create and activate a virtual environment for MacOS, WSL, or Linux
1. python3 -m venv rep-g
2. source rep-g/bin/activate

### Create and activate a virtual environment on Anaconda
1. anaconda env create -n rep-g

### Install and run the application
Run the following commands:
1. "pip install -r requirements.txt" (NOTE: This may take some time, especially on Anaconda or Windows systems.)
2. "python src/visualization/app.py"

To view the application, navigate to http://127.0.0.1:8050/ in the browser of your choice.

## EXECUTION

Upon opening the app, follow the instructions to use it:
1. From the dropdown on the top, select a topic.
2. Select a subtopic (node) on the graph on the upper left.
3. Select a piece of the pie chart on the upper right.
4. Visualizations of that cluster will be displayed on the bottom panel - specifically, statistics of the cluster computed from our knowledge graph. Feel free to move your mouse around to reveal tooltips.

## DEMO VIDEO

Link: https://youtu.be/p3PS2A4KMX8
