import pandas as pd
import plotly.express as px
import numpy as np
import csv

# data wrangling
df = pd.read_csv('../datasets/toronto_data.csv')
df['cases_oct12'] = df['outbreak_cases_oct12'] + df['cases_60+_oct12'] + df['cases_50+_oct12'] + df[
    'cases_less_than_50_oct12'] + df['hospitalized_cases_oct12'] + df['MALE_cases_oct12'] + df['FEMALE_cases_oct12']
df["date"] = "oct_12"
df["cases"] = 0
df = pd.concat([df] * 2, ignore_index=True)
df.loc[df.index >= 140, "date"] = "aug_31"
df['cases'] = np.where(df.date == 'aug_31', df.sporadic_cases_aug31, df.cases_oct12)
df["ratio"] = df["cases"] / df["population"]
# change the neighbourhood name for different stats:
df_1 = df[df['Neighbourhood_name'] == 'West Humber-Clairville']

population = int(input("population"))
cases_oct = int(input("cases_oct"))
cases_aug = int(input("cases_aug"))

new_row_oct = {'_id': 141, 'Neighbourhood_name': "sample", 'neighbourhood_id': "sample", 'population': population,
               'population_density': 0, 'neighbourhood_area': 0, 'percent_less_than_LIM': 0,
               'percent_less_than_LICO': 0, 'percent_unemployed': 0,
               'percent_less_than_high_school': 0, 'percent_crowded_housing': 0,
               'percent_people_of_colour': 0, 'percent_black': 0, 'percent_south_asian': 0,
               'percent_non_english_french': 0, 'percent_over_65': 0, 'percent_over_85': 0,
               'percent_public_transit': 0, 'percent_non_mover': 0, 'percent_health_occ': 0,
               'percent_health_soc_service_ind': 0, 'pm25_2016': 0, 'mean_pm25_2000_2016': 0,
               'no2_2016': 0, 'mean_no2_2000_2016': 0, 'greenness_2016': 0,
               'mean_greenness_2000_2016': 0, 'DA_weighted_pm25_2016': 0,
               'DA_weighted_no2_2016': 0, 'DA_weighted_greenness_2016': 0,
               'DA_weighted_ros_2016': 0,
               'above_below_median_percent_less_than_high_school': 0,
               'above_below_median_percent_crowded_housing': 0,
               'above_below_median_percent_black': 0, 'percent_less_than_LICO_tertile': 0,
               'percent_people_of_colour_tertile': 0,
               'percent_less_than_high_school_tertile': 0,
               'percent_crowded_housing_tertile': 0, 'percent_health_occ_tertile': 0,
               'percent_black_tertile': 0, 'percent_health_soc_serv_ind_tertile': 0,
               'highest_tertile_percent_health_occ_low_income': 0,
               'highest_tertile_percent_health_soc_serv_ind_low_income': 0,
               'highest_tertile_percent_health_occ_people_of_colour': 0,
               'highest_tertile_percent_health_soc_serv_ind_people_of_colour': 0,
               'sporadic_cases_aug31': 0, 'days_since_peak_aug31': 0,
               'days_since_1st_case_aug31': 0, 'mean_neighbouring_incidence_aug31': 0,
               'sporadic_cases_oct12': 0, 'mean_neighbouring_incidence_oct12': 0,
               'days_since_peak_oct12': 0, 'days_since_1st_case_oct12': 0, 'incidence_oct12': 0,
               'FEMALE_cases_oct12': 0, 'MALE_cases_oct12': 0, 'hospitalized_cases_oct12': 0,
               'cases_less_than_50_oct12': 0, 'cases_50+_oct12': 0, 'cases_60+_oct12': 0,
               'outbreak_cases_oct12': 0, 'tests_per_1k': 0, 'cases_oct12': 0, 'date': "oct_12", 'cases': cases_oct,
               'ratio': cases_oct / population}

new_row_aug = {'_id': 141, 'Neighbourhood_name': "sample", 'neighbourhood_id': "sample", 'population': population,
               'population_density': 0, 'neighbourhood_area': 0, 'percent_less_than_LIM': 0,
               'percent_less_than_LICO': 0, 'percent_unemployed': 0,
               'percent_less_than_high_school': 0, 'percent_crowded_housing': 0,
               'percent_people_of_colour': 0, 'percent_black': 0, 'percent_south_asian': 0,
               'percent_non_english_french': 0, 'percent_over_65': 0, 'percent_over_85': 0,
               'percent_public_transit': 0, 'percent_non_mover': 0, 'percent_health_occ': 0,
               'percent_health_soc_service_ind': 0, 'pm25_2016': 0, 'mean_pm25_2000_2016': 0,
               'no2_2016': 0, 'mean_no2_2000_2016': 0, 'greenness_2016': 0,
               'mean_greenness_2000_2016': 0, 'DA_weighted_pm25_2016': 0,
               'DA_weighted_no2_2016': 0, 'DA_weighted_greenness_2016': 0,
               'DA_weighted_ros_2016': 0,
               'above_below_median_percent_less_than_high_school': 0,
               'above_below_median_percent_crowded_housing': 0,
               'above_below_median_percent_black': 0, 'percent_less_than_LICO_tertile': 0,
               'percent_people_of_colour_tertile': 0,
               'percent_less_than_high_school_tertile': 0,
               'percent_crowded_housing_tertile': 0, 'percent_health_occ_tertile': 0,
               'percent_black_tertile': 0, 'percent_health_soc_serv_ind_tertile': 0,
               'highest_tertile_percent_health_occ_low_income': 0,
               'highest_tertile_percent_health_soc_serv_ind_low_income': 0,
               'highest_tertile_percent_health_occ_people_of_colour': 0,
               'highest_tertile_percent_health_soc_serv_ind_people_of_colour': 0,
               'sporadic_cases_aug31': 0, 'days_since_peak_aug31': 0,
               'days_since_1st_case_aug31': 0, 'mean_neighbouring_incidence_aug31': 0,
               'sporadic_cases_oct12': 0, 'mean_neighbouring_incidence_oct12': 0,
               'days_since_peak_oct12': 0, 'days_since_1st_case_oct12': 0, 'incidence_oct12': 0,
               'FEMALE_cases_oct12': 0, 'MALE_cases_oct12': 0, 'hospitalized_cases_oct12': 0,
               'cases_less_than_50_oct12': 0, 'cases_50+_oct12': 0, 'cases_60+_oct12': 0,
               'outbreak_cases_oct12': 0, 'tests_per_1k': 0, 'cases_oct12': 0, 'date': "aug_31", 'cases': cases_aug,
               'ratio': cases_aug / population}

# append row to the dataframe
df = df.append(new_row_oct, ignore_index=True)
df = df.append(new_row_aug, ignore_index=True)
df = df.sort_values(by="date")
print(df)

# change the neighbourhood name for different stats:
# df_1= df.loc[df['Neighbourhood_name'].isin(['sample','University'])]
# print(df_1)
fig = px.line(df, x='date', y='ratio', color='Neighbourhood_name', title='Covid Sim Data', labels={
    "date": "month(duration points)",
    "ratio": "number of cases/ population",
    "Neighbourhood_name": "Neighbourhood"
}, )
fig.show()
