# Election Night Classification
* Checkout of the most recent model run [here](final_project_checkin_template.ipynb). 

Final Project for MSDS621 - Intro to Machine Learning<br>
Univeristy of San Francisco <br>
Master of Science Data Science

## Contributors
* [Nicole Kacirek](https://github.com/nkacirek1)
* [Lance Fernando](https://github.com/Ljfernando)
* [Sarah Melancon](https://github.com/smelancon)

## Research Question
Can we use presidential election data to predict midterm election results? Specifically, can we classify a race as win for the Democratic or Republican candiadate?

## Data
We built our data set from ground up, collecting 2012-2014 / 2016-2018 precinct level election results from a variarty of Secretary of State websites. We then worked with domain experts to create useful features. 

* Our final dataset can be found [here](data/final.csv).
* For more information on how we transformed our [raw votes totals](data) into features, checkout the [source code](src).

## Methods
* Data pre-processing:
  - scikit-learn LabelEncoder
  - scikit-learn train_test_split
* Model:
  - scikit-learn DecisionTreeClassifier

## Evaluation
Our current classifer has an accuracy of 90% on our testing set. 
