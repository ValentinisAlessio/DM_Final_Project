# Data Management Final Project

**Authors:**
| Name | Surname | email | Master |
|:---:|:---:|:---:|:---:|
| Sara | Carpenè | SARA.CARPENE@studenti.units.it | DSAI |
| Alessio | Valentinis | ALESSIO.VALENTINIS@studenti.units.it | DSAI |
| Marco | Zampar | MARCO.ZAMPAR@studenti.units.it | DSAI |

**Date:**
- 2024-07

This repository ontains the code, results and plots relative to the Data Management exam within the [Data Science and Artificial Intelligence Master Program](https://dsai.units.it/), held at University of Trieste.

All the results are explained in the [report](./DW_CS.pdf)

## How to reproduce the results.

### Requirements

The scripts were designed and tested with the MacOS operating system.  They are completely compatible with the Linux environment, so if running on Windows, make sure to use WSL.

The following software is required to run the scripts:

- [PostgreSQL](https://www.postgresql.org/) (tested with version 16.2)
- [Python](https://www.python.org/) (tested with version 3.11.4)\
  With the following libraries:
    - [pandas](https://pandas.pydata.org/)
    - [numpy](https://numpy.org/)
    - [psycopg2](https://www.psycopg.org/)

### Steps

1. Clone the repository:
    ```bash
    git clone git@github.com:ValentinisAlessio/DM_Final_Project.git
    ```

2. Initialize the database by running the `init_db.ipynb` notebook.
**ATTENTION:** In the script, for the bigger tables, we provided also a "*slim population*", that require less RAM. So run solely the chunks you need.

3. For index generation and population of materializations, the notebooks `query.ipynb` and `materialize.ipynb` were used, also to evaluate the Execution plan of the queries.

Automatic benchmark was done using the `<base/idx/materialize/materialize_index>_benchmark.py` scripts.