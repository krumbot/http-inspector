# HTTP-Inspector
#### Dependency Installation
`virtualenv env`
`source env/bin/activate`
`pip install -r requirements.txt`

#### Running Tests
The tests for this project are in the tests/ folder. To run the tests, install dependencies and run:
`pytest tests/`

#### Running the Application
To run the application, install dependencies and run:
`sudo python src/main.py`

To change the minimum critical threshold (i.e. the minimum number of hits within a two minute span before the inspector's status changes from "Healthy" to "Critical"), use the `--critical-traffic` flag. For example, the following command will run the http-inspector application with a minimum critical threshold of 500 hits/last 2 min:

`sudo python src/main.py --critical-traffic=500`