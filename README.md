# Midterm Election Classification
* Checkout of the most recent [model run](experiments/Final_Model_Run.ipynb) and the [final presenation](https://docs.google.com/presentation/d/1g5ipS_9XV3nwQz-FQDJTJi3o_W2bv-dxbK2Yd1gWkGw/edit?usp=sharing).

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

* Our final datasets can be found [here](full_data).
* Our partially reporting simulation datasets can be found [here](partial_data).
* For more information on how we transformed our [raw votes totals](full_data) into features, checkout the [source code](src).

## Methods
* Data pre-processing:
  - scikit-learn LabelEncoder
  - scikit-learn LeaveOneOut cross validation
  - oversample tight races
* Model:
  - scikit-learn DecisionTreeClassifier
  - scikit-learn RandomForestClassifier
  - scikit-learn GradientBoostingClassifier

## Evaluation
Our best classifer is GradientBoostingClassifier. It has an average accuracy of 86.8% on our testing set, and 92.2% on the tight races within the testing set.

## Final Presentation
Slide deck for [final presenation](https://docs.google.com/presentation/d/1g5ipS_9XV3nwQz-FQDJTJi3o_W2bv-dxbK2Yd1gWkGw/edit?usp=sharing).
