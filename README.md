# Insurance - PREDICTION SYSTEM

The task is to predict the response of insurance for each case

1. The first step involves exploratory data analysis (EDA), conducted in a Jupyter notebook.
2. The second step encompasses data pre-processing, feature engineering, model training, and prediction based on historical data. Multiple algorithms were experimented with to determine the most suitable model. Probability scores were weighted against the models' accuracy values to derive the final score. Subsequently, probability scores were classified as binary based on different predefined threshold values.
3. The third step involves processing the methods identified in the second step for an Excel file. Initially, using the OpenAI library, "Named Entity Recognition" was performed on descriptions in the Excel file to extract features. The extracted features were then utilized in the algorithmic solution developed in the second step to make predictions.
4. Finally, in the fourth step, a REST API was developed, and the solutions were made available to users through different methods.

In this solution, 5 different machine learning algorithms were used. After the predictions, a scoring algorithm was developed that was weighted according to the accuracy rates of each model. This score, recorded as 'response_score' in the result file, is a probability score.

Again after prediction, you can create rest api to see results. "main.py" folder was created for rest service. In this step for easy and fast execution, I prefer to dockerize the service. For dockerization, you have to run below commands on terminal.

*** For model training, you have to run "03-Enrian-model.ipynb"

*** For model service, you have to run "python main.py" on terminal

However, I highly recommend to use dockerize flask service version with help of below shell scripts

1) docker build --tag enrian-response-app:1.0 .
2) docker run -p 1001:1001 --name enrian-response-app enrian-response-app:1.0

After this process, you can use Postman to test. You can find postman file under "collection" file. You have to import that json file to the Postman. 

**Services:**

(get_prediction) : This get method return probability values for specific id. This method need id as a parameter. 
(get_random_records) : This get method return 50 id's probability values. This method need username and password as a parameter. 
(post_predictions) : This post method return predictions for customer in description excel file. This method need username and password as a parameter.