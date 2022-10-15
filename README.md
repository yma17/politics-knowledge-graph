# REP-G: Representing Emerging Politics with Graphs

(add description)

## Directory structure

This is a description of the directory structure of this repository.

- `data/`: any locally stored data (raw/preprocessed) used for our project.
    - (there is a `.gitignore` in this folder that prevents any other files inside it from being committed)
    - (let's store our data elsewhere; it is not good practice to commit it into the repository)
- `src/`: all implementation code.
    - `data_retrieval/`: retrieve (and preprocess) data  (e.g. from ProPublica Congress API).
    - `knowledge_graph/`: define, construct, and populate knowledge graph.
    - `community_detection/`: perform community detection on knowledge graph.
    - `topic_modelling/`: perform topic modelling on knowledge graph.
    - `visualization/`: implementation for application for interactive visualization.

To keep the repo organized, please only place files relevant to each description above in each respective folder.