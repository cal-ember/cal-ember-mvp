# 🔥 CalEmber: Fire Damage Prediction & Insurance Assessment Tool



## 📝 Description  
Calember is a machine learning-powered tool designed to assess fire damage risk for insurance policies. By analyzing structural and environmental attributes, it provides damage classification and enhances risk assessment for current and potential California homeowners.

![Demo](https://github.com/cal-ember/cal-ember-mvp/blob/master/cal_ember.gif)

## 🔗 Links
- [Capstone Project Page](https://www.ischool.berkeley.edu/projects/2024/calember-fire-damage-prediction-insurance-assessment-tool)
- [Model Code](https://github.com/cal-ember/cal-ember-mvp/tree/master)

## 💡 Features  
- ✅ Predicts fire damage severity based on property attributes  
- ✅ Uses advanced machine learning models for classification  
- ✅ Enables potential and current homeowners to assess risk effectively  
- ✅ Provides a user-friendly interface for damage classification  
- ✅ **Interactive Tableau Dashboards** for data visualization  

## 🛠️ Built with  
- **Backend:** Python, Flask, AWS SageMaker  
- **Frontend:** HTML, CSS, JavaScript  
- **Machine Learning:** Scikit-learn, XGBoost, Pandas, NumPy  
- **Deployment:** Heroku  
- **Data Visualization:** Tableau  

## 📊 Models Used  
- XGBoost (Final Model)
- LightGBM  
- Random Forest  
- Logistic Regression  

## 📂 Dataset  
- Includes structural and environmental data for fire damage prediction  
- Features: property attributes, fire history, environmental factors  

## 📊 Tableau Dashboards  
### 🔥 Damage Map Dashboard  
Explore historical median property damage levels caused by wildfires per zip code.  
**[View Dashboard](https://public.tableau.com/views/DS210ACalEmberDamagesMap/DamageMapDashboard)**  

### 🏡 Insurance Map Dashboard  
Explore historical insurance data, including policies and coverages, filtered by home type and year.  
**[View Dashboard](https://public.tableau.com/views/DS210ACalEmberInsuranceMapDashboard/InsuranceMapDashboard)**  

### 📈 Insurance Trends Over Time Dashboard  
Analyze insurance trends over time for specific zip codes and home types, comparing year-over-year changes.  
**[View Dashboard](https://public.tableau.com/views/DS210ACalEmberInsuranceTrendsOverTime/InsuranceTrendsOverTimeDashboard)**  

## 👥 Contributors  
- **Michelle Cheung** [(@mcheung-cal)](https://github.com/mcheung-cal)  
- **Ishika Prashar** [(@ishikaprashar)](https://github.com/ishikaprashar)  
- **Hao Xie** [(@haoxie912)](https://github.com/haoxie912)  
- **Jackie Wang** [(@jackieeewang)](https://github.com/jackieeewang) 


## Setup Instructions

1. Clone the repository:
  ```bash
   git clone https://github.com/your-org/your-repo.git
   ```

2. (optional) Activate virtual environment
 ``` 
  python3 -m venv env
  source env/bin/activate
```
3. Install required dependencies
  ```
   pip install -r requirements.txt
   ```
4. To run, either run
```
python app.py
```
or
```
flask run
```

 

